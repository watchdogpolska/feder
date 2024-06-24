import inspect
import json
import logging
import time

from django.conf import settings
from django.db import models
from django.db.models.functions import Substr
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import TokenTextSplitter
from langchain_community.callbacks import get_openai_callback
from langchain_openai import AzureChatOpenAI
from model_utils import Choices
from model_utils.models import TimeStampedModel

from feder.letters.utils import html_to_text
from feder.main.utils import FormattedDatetimeMixin

from .llm_tools import get_serializable_dict, num_tokens_from_string
from .prompts import (
    NORMALIZED_RESPONSE_ANSWER_KEY,
    NORMALIZED_RESPONSE_QUESTION_KEY,
    EMAIL_CTEGORISATiON_REFUSED,
    answer_categorization,
    letter_categorization,
    letter_evaluation_intro,
    letter_response_normalization,
    monitoring_response_normalized_template,
)

logger = logging.getLogger(__name__)


class LLmRequestQuerySet(FormattedDatetimeMixin, models.QuerySet):
    def queued(self):
        return self.filter(status=self.model.STATUS.queued)


# TODO: add LLM engine setup method for DRY code and  better tokens limits management
class LlmRequest(TimeStampedModel):
    STATUS = Choices(
        (0, "created", _("Created")),
        (1, "queued", _("Queued")),
        (2, "done", _("Done")),
        (3, "failed", _("Failed")),
    )
    name = models.CharField(
        max_length=100, verbose_name=_("Name"), null=True, blank=True
    )
    args = models.JSONField(verbose_name=_("Arguments"), null=True, blank=True)
    engine_name = models.CharField(
        max_length=20, verbose_name=_("LLM Engine name"), null=True, blank=True
    )
    status = models.IntegerField(choices=STATUS, default=STATUS.created)
    request_prompt = models.TextField(
        verbose_name=_("LLM Engine request"), null=True, blank=True
    )
    response = models.TextField(
        verbose_name=_("LLM Engine response"), null=True, blank=True
    )
    token_usage = models.JSONField(
        verbose_name=_("LLM Engine token usage"), null=True, blank=True
    )
    objects = LLmRequestQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def completion_time(self):
        if self.token_usage:
            return float(self.token_usage.get("completion_time", 0))
        return 0

    @property
    def completion_time_str(self):
        value = self.completion_time
        if value < 1:
            return f"{value:.2f}s"
        elif value < 10:
            return f"{value:.1f}s"
        return f"{value:.0f}s"

    @property
    def tokens_used(self):
        if self.token_usage:
            return self.token_usage.get("total_tokens", 0)
        return 0

    @property
    def cost(self):
        if self.token_usage:
            return float(self.token_usage.get("total_cost", 0))
        return 0

    @property
    def cost_str(self):
        return f"${self.cost:.5f}"

    @property
    def response_text(self):
        if self.response:
            try:
                value = json.loads(
                    self.response.replace("'", '"').replace("\n", "")
                ).get("output_text", "")
                return value
            except json.JSONDecodeError:
                return self.response
        return ""


class LlmLetterRequest(LlmRequest):
    evaluated_letter = models.ForeignKey(
        "letters.Letter",
        on_delete=models.PROTECT,
        verbose_name=_("Evaluated Letter"),
    )

    @classmethod
    def categorize_letter(cls, letter):
        # llm_engine = settings.OPENAI_API_ENGINE_35
        llm_engine = settings.OPENAI_API_ENGINE_4
        institution_name = ""
        monitoring_template = ""
        max_engine_tokens = min(
            settings.OPENAI_API_ENGINE_4_MAX_TOKENS,
            settings.LETTER_CATEGORIZATION_MAX_TOKENS,
        )
        if letter.case and letter.case.monitoring:
            institution_name = letter.case.institution.name
            monitoring_template = html_to_text(letter.case.monitoring.template)
            monitoring_template_tokens = num_tokens_from_string(
                monitoring_template, llm_engine
            )
            if monitoring_template_tokens > (max_engine_tokens // 3 * 2):
                text_splitter = TokenTextSplitter(
                    chunk_size=(max_engine_tokens // 3 * 2), chunk_overlap=0
                )
                texts = text_splitter.split_text(monitoring_template)
                monitoring_template = texts[0] + "... (tekst skrócony)"
                logger.warning(
                    "Monitoring template text too long for LLM engine: "
                    + f"{monitoring_template_tokens} tokens. Using only first 66%."
                )
        intro = letter_evaluation_intro.format(
            institution=institution_name,
            monitoring_question=monitoring_template,
        )
        test_prompt = letter_categorization.format(
            intro=intro,
            institution=institution_name,
            monitoring_response="",
        )

        q_tokens = num_tokens_from_string(test_prompt, llm_engine)
        # print(f"q_tokens: {q_tokens}")

        max_tokens = max_engine_tokens - q_tokens - 500
        # print(f"max_tokens: {max_tokens}")
        text_splitter = TokenTextSplitter(
            chunk_size=max_tokens, chunk_overlap=min(max_tokens // 2, 100)
        )
        texts = text_splitter.split_text(letter.get_full_content())
        # print(
        #     "texts[0] tokens:",
        #     num_tokens_from_string(texts[0], llm_engine),
        # )
        final_prompt = letter_categorization.format(
            intro=intro,
            institution=institution_name,
            monitoring_response=texts[0],
        )
        letter_llm_request = cls.objects.create(
            name=inspect.currentframe().f_code.co_name,
            args={"letter_pk": letter.pk},
            evaluated_letter=letter,
            engine_name=llm_engine,
            request_prompt=final_prompt,
            status=cls.STATUS.created,
            response="",
            token_usage={},
        )
        letter_llm_request.save()
        model = AzureChatOpenAI(
            openai_api_type=settings.OPENAI_API_TYPE,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_ENDPOINT,
            deployment_name=llm_engine,
            temperature=settings.OPENAI_API_TEMPERATURE,
        )
        chain = letter_categorization | model | StrOutputParser()
        start_time = time.time()
        with get_openai_callback() as cb:
            try:
                resp = chain.invoke(
                    {
                        "intro": intro,
                        "institution": institution_name,
                        "monitoring_response": texts[0],
                    }
                )
            except ValueError as e:
                if "content filter being triggered" in str(e):
                    logger.error(
                        f"Error in categorizing letter {letter.pk}: {e}."
                        + " Content filter being triggered."
                    )
                    resp = EMAIL_CTEGORISATiON_REFUSED
                else:
                    raise e
        end_time = time.time()
        execution_time = end_time - start_time
        llm_info_dict = get_serializable_dict(cb)
        llm_info_dict["completion_time"] = execution_time
        letter_llm_request.response = resp
        letter_llm_request.token_usage = llm_info_dict
        letter_llm_request.status = cls.STATUS.done
        letter_llm_request.save()
        letter.ai_evaluation = resp
        if "F) email nie jest odpowiedzią" in resp and "jest spamem" in resp:
            letter.is_spam = letter.SPAM.probable_spam
        letter.save()
        # TODO: add case.response_received update
        # print(f"resp: {resp}")
        # print(f"cb: {cb}")
        # print(f"execution_time: {execution_time}")

    @classmethod
    def get_normalized_answers(cls, letter):
        institution_name = ""
        normalized_questions_json = ""
        if letter.case and letter.case.monitoring:
            institution_name = letter.case.institution.name
            if not letter.case.monitoring.normalized_response_template:
                logger.warning(
                    "Can not get normalised answer: normalized_response_template"
                    + f" missing in monitoring {letter.case.monitoring.pk}"
                )
                return
            if not letter.case.monitoring.use_llm:
                logger.warning(
                    "Skipping normalised answer: use_llm is False in monitoring"
                    + f" {letter.case.monitoring.pk}"
                )
                return
            normalized_questions_json = (
                letter.case.monitoring.normalized_response_template
            )
            instruction_extension = (
                letter.case.monitoring.letter_normalization_prompt_extension or ""
            )
        else:
            logger.warning(
                f"Can not get normalised answer: letter {letter.pk}"
                + " has no case or monitoring."
            )
            return
        test_prompt = letter_response_normalization.format(
            institution=institution_name,
            normalized_questions=normalized_questions_json,
            prompt_instruction_extension=instruction_extension,
            monitoring_response="",
        )
        # llm_engine = settings.OPENAI_API_ENGINE_35
        llm_engine = settings.OPENAI_API_ENGINE_4
        q_tokens = num_tokens_from_string(test_prompt, llm_engine)
        # print(f"q_tokens: {q_tokens}")

        max_tokens = (
            min(
                # settings.OPENAI_API_ENGINE_35_MAX_TOKENS,
                settings.OPENAI_API_ENGINE_4_MAX_TOKENS,
                settings.LETTER_NORMALIZATION_MAX_TOKENS,
            )
            - q_tokens
            - 500
        )
        # print(f"max_tokens: {max_tokens}")
        text_splitter = TokenTextSplitter(chunk_size=max_tokens, chunk_overlap=100)
        texts = text_splitter.split_text(letter.get_full_content())
        # print(
        #     "texts[0] tokens:",
        #     num_tokens_from_string(texts[0], llm_engine),
        # )
        model = AzureChatOpenAI(
            openai_api_type=settings.OPENAI_API_TYPE,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_ENDPOINT,
            deployment_name=llm_engine,
            temperature=settings.OPENAI_API_TEMPERATURE,
        )
        chain = letter_response_normalization | model | StrOutputParser()
        for text in texts:
            final_prompt = letter_response_normalization.format(
                institution=institution_name,
                normalized_questions=normalized_questions_json,
                prompt_instruction_extension=instruction_extension,
                monitoring_response=text,
            )
            letter_llm_request = cls.objects.create(
                name=inspect.currentframe().f_code.co_name,
                args={"letter_pk": letter.pk},
                evaluated_letter=letter,
                engine_name=llm_engine,
                request_prompt=final_prompt,
                status=cls.STATUS.created,
                response="",
                token_usage={},
            )
            letter_llm_request.save()
            start_time = time.time()
            with get_openai_callback() as cb:
                resp = chain.invoke(
                    {
                        "institution": institution_name,
                        "normalized_questions": normalized_questions_json,
                        "monitoring_response": text,
                    }
                )
            end_time = time.time()
            execution_time = end_time - start_time
            llm_info_dict = get_serializable_dict(cb)
            llm_info_dict["completion_time"] = execution_time
            letter_llm_request.response = resp
            letter_llm_request.token_usage = llm_info_dict
            letter_llm_request.status = cls.STATUS.done
            letter_llm_request.save()
            normalized_questions_json = resp
        letter.normalized_response = normalized_questions_json
        letter.save()
        return normalized_questions_json

    @classmethod
    def categorize_answer(self, letter, question_number):
        institution_name = ""
        if letter.case and letter.case.monitoring:
            institution_name = letter.case.institution.name
            if not letter.case.monitoring.use_llm:
                logger.warning(
                    f"Skipping normalising answer for letter {letter.pk}:"
                    + ": use_llm is False in monitoring"
                    + f" {letter.case.monitoring.pk}"
                )
                return
            if not letter.case.monitoring.normalized_response_template:
                logger.warning(
                    f"Can not categorize answer for letter {letter.pk}:"
                    + ": normalized_response_template"
                    + f" missing in monitoring {letter.case.monitoring.pk}"
                )
                return
            if not letter.case.monitoring.normalized_response_answers_categories:
                logger.warning(
                    f"Can not categorize answer for letter {letter.pk}:"
                    + " normalized_response_answers_categories"
                    + f" missing in monitoring {letter.case.monitoring.pk}"
                )
                return
            if not letter.normalized_response:
                logger.warning(
                    f"Can not categorize answer for letter {letter.pk}:"
                    + ": normalized_response"
                    + f" missing in letter {letter.pk}"
                )
                return
            question_and_answer_dict = letter.get_normalized_question_and_answer_dict(
                question_number
            )
            if not question_and_answer_dict.get(
                NORMALIZED_RESPONSE_QUESTION_KEY, None
            ) or not question_and_answer_dict.get(NORMALIZED_RESPONSE_ANSWER_KEY, None):
                logger.warning(
                    f"Can not categorize answer for letter {letter.pk}: question or"
                    + f" answer missing for letter {letter.pk} and question"
                    + f' "{question_number}"'
                )
                return
            categories_update_time = (
                letter.case.monitoring.get_categories_update_time_for_question(
                    question_number
                )
            )
            categorization_already_done = self.objects.filter(
                name=inspect.currentframe().f_code.co_name,
                evaluated_letter=letter,
                args__question_number=question_number,
                created__gt=categories_update_time,
            ).first()
            if categorization_already_done:
                logger.info(
                    f"Skipping categorization for letter {letter.pk} and question"
                    + f' "{question_number}" as already done: '
                    + f"{categorization_already_done.args} at "
                    + f"{categorization_already_done.created}."
                )
                return
            question = question_and_answer_dict[NORMALIZED_RESPONSE_QUESTION_KEY]
            answer = question_and_answer_dict[NORMALIZED_RESPONSE_ANSWER_KEY]
            answer_categories = (
                letter.case.monitoring.get_answer_categories_for_question(
                    question_number
                )
            )
            if not answer_categories:
                logger.warning(
                    "Can not categorize answer: answer_categories"
                    + f" missing in monitoring {letter.case.monitoring.pk}"
                    + f" for question {question_number}"
                )
                return
        else:
            logger.warning(
                f"Can not categorize answer: letter {letter.pk}"
                + " has no case or monitoring."
            )
            return
        prompt = answer_categorization.format(
            institution=institution_name,
            question=question,
            answer=answer,
            answer_categories=answer_categories,
        )
        llm_engine = settings.OPENAI_API_ENGINE_35
        prompt_tokens = num_tokens_from_string(prompt, llm_engine)
        # print(f"q_tokens: {q_tokens}")
        max_tokens = min(settings.OPENAI_API_ENGINE_35_MAX_TOKENS, 12000)
        if prompt_tokens > max_tokens:
            message = (
                f"Prompt tokens {prompt_tokens} exceed max tokens {max_tokens}."
                + f"for letter {letter.pk} and question {question_number}"
            )
            logger.warning(message)
            return
        letter_llm_request = self.objects.create(
            name=inspect.currentframe().f_code.co_name,
            args={"letter_pk": letter.pk, "question_number": question_number},
            evaluated_letter=letter,
            engine_name=llm_engine,
            request_prompt=prompt,
            status=self.STATUS.created,
            response="",
            token_usage={},
        )
        letter_llm_request.save()
        model = AzureChatOpenAI(
            openai_api_type=settings.OPENAI_API_TYPE,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_ENDPOINT,
            deployment_name=llm_engine,
            temperature=settings.OPENAI_API_TEMPERATURE,
        )
        chain = answer_categorization | model | StrOutputParser()
        start_time = time.time()
        with get_openai_callback() as cb:
            resp = chain.invoke(
                {
                    "institution": institution_name,
                    "question": question,
                    "answer": answer,
                    "answer_categories": answer_categories,
                }
            )
        end_time = time.time()
        execution_time = end_time - start_time
        llm_info_dict = get_serializable_dict(cb)
        llm_info_dict["completion_time"] = execution_time
        letter_llm_request.response = resp
        letter_llm_request.token_usage = llm_info_dict
        letter_llm_request.status = self.STATUS.done
        letter_llm_request.save()
        letter.set_normalized_answer_category(question_number, resp)


class LlmMonitoringRequest(LlmRequest):
    evaluated_monitoring = models.ForeignKey(
        "monitorings.Monitoring",
        on_delete=models.PROTECT,
        verbose_name=_("Evaluated Monitoring"),
    )
    chat_request = models.BooleanField(
        verbose_name=_("Chat Request"), default=False, blank=True
    )

    @classmethod
    def get_response_normalized_template(cls, monitoring):
        if not monitoring.use_llm:
            logger.info(
                f"Monitoring pk={monitoring.pk} not using LLM - skipping normalization."
            )
            return
        final_prompt = monitoring_response_normalized_template.format(
            monitoring_template=monitoring.template,
        )
        llm_engine = settings.OPENAI_API_ENGINE_35
        monitoring_llm_request = cls.objects.create(
            name=inspect.currentframe().f_code.co_name,
            args={"monitoring_pk": monitoring.pk},
            evaluated_monitoring=monitoring,
            engine_name=llm_engine,
            request_prompt=final_prompt,
            status=cls.STATUS.created,
            response="",
            token_usage={},
        )
        monitoring_llm_request.save()
        model = AzureChatOpenAI(
            openai_api_type=settings.OPENAI_API_TYPE,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_ENDPOINT,
            deployment_name=llm_engine,
            temperature=settings.OPENAI_API_TEMPERATURE,
        )
        chain = monitoring_response_normalized_template | model | StrOutputParser()
        start_time = time.time()
        with get_openai_callback() as cb:
            resp = chain.invoke({"monitoring_template": monitoring.template})
        end_time = time.time()
        execution_time = end_time - start_time
        llm_info_dict = get_serializable_dict(cb)
        llm_info_dict["completion_time"] = execution_time
        monitoring_llm_request.response = resp
        monitoring_llm_request.token_usage = llm_info_dict
        monitoring_llm_request.status = cls.STATUS.done
        monitoring_llm_request.save()
        monitoring.normalized_response_template = resp
        monitoring.save()


class LlmMonthlyCost(TimeStampedModel):
    year_month = models.CharField(
        max_length=20, verbose_name=_("Month"), null=True, blank=True
    )
    engine_name = models.CharField(
        max_length=20, verbose_name=_("LLM Engine name"), null=True, blank=True
    )
    cost = models.FloatField(verbose_name=_("Cost"))

    class Meta:
        verbose_name = _("LLM Monthly Cost")
        verbose_name_plural = _("LLM Monthly Cost")

    @classmethod
    def get_costs_dict(cls):
        llm_letters_costs = list(
            LlmLetterRequest.objects.all()
            .with_formatted_datetime("created", timezone.get_default_timezone())
            .annotate(
                year_month=Substr("created_str", 1, 7),
            )
            .values(
                "created_str",
                "year_month",
                "engine_name",
                "token_usage",
            )
        )
        llm_monitorings_costs = list(
            LlmMonitoringRequest.objects.all()
            .with_formatted_datetime("created", timezone.get_default_timezone())
            .annotate(
                year_month=Substr("created_str", 1, 7),
            )
            .values(
                "created_str",
                "year_month",
                "engine_name",
                "token_usage",
            )
        )
        llm_costs = llm_letters_costs + llm_monitorings_costs
        cost_months = sorted(list({x["year_month"] for x in llm_costs}))
        llm_engines = sorted(list({x["engine_name"] for x in llm_costs}))
        llm_monthly_costs = [
            {
                "year_month": y_m,
                "engine_name": e_n,
                "cost": 0.0,
            }
            for y_m in cost_months
            for e_n in llm_engines
        ]
        id = 0
        for llm_cost in llm_monthly_costs:
            id += 1
            year_month = llm_cost["year_month"]
            engine_name = llm_cost["engine_name"]
            llm_cost["id"] = id
            llm_cost["cost"] = sum(
                [
                    float(x["token_usage"].get("total_cost", 0))
                    for x in llm_costs
                    if x["year_month"] == year_month and x["engine_name"] == engine_name
                ]
            )
        return llm_monthly_costs


class LlmMonitoringCost(TimeStampedModel):
    monitoring_id = models.IntegerField(verbose_name=_("Monitoring ID"))
    monitoring_name = models.CharField(
        max_length=100, verbose_name=_("Monitoring Name"), null=True, blank=True
    )
    engine_name = models.CharField(
        max_length=20, verbose_name=_("LLM Engine name"), null=True, blank=True
    )
    cost = models.FloatField(verbose_name=_("Cost"))

    class Meta:
        verbose_name = _("LLM Cost Per Monitoring")
        verbose_name_plural = _("LLM Costs Per Monitoring")

    @classmethod
    def get_costs_dict(cls):
        llm_letters_costs = list(
            LlmLetterRequest.objects.all()
            .annotate(
                monitoring_id=models.F(
                    "evaluated_letter__record__case__monitoring__id"
                ),
                monitoring_name=models.F(
                    "evaluated_letter__record__case__monitoring__name"
                ),
            )
            .values(
                "monitoring_id",
                "monitoring_name",
                "engine_name",
                "token_usage",
            )
        )
        llm_monitorings_costs = list(
            LlmMonitoringRequest.objects.all()
            .annotate(
                monitoring_id=models.F("evaluated_monitoring__id"),
                monitoring_name=models.F("evaluated_monitoring__name"),
            )
            .values(
                "monitoring_id",
                "monitoring_name",
                "engine_name",
                "token_usage",
            )
        )
        llm_costs = llm_letters_costs + llm_monitorings_costs
        monitorings = sorted(list({x["monitoring_id"] or 0 for x in llm_costs}))
        llm_engines = sorted(list({x["engine_name"] for x in llm_costs}))
        llm_monitorings_costs = [
            {
                "monitoring_id": m_id,
                "engine_name": e_n,
                "cost": 0.0,
            }
            for m_id in monitorings
            for e_n in llm_engines
        ]
        id = 0
        for llm_cost in llm_monitorings_costs:
            id += 1
            monitoring_id = llm_cost["monitoring_id"]
            engine_name = llm_cost["engine_name"]
            llm_cost["id"] = id
            llm_cost["monitoring_name"] = next(
                (
                    x["monitoring_name"]
                    for x in llm_costs
                    if x["monitoring_id"] == monitoring_id
                ),
                "",
            )
            llm_cost["cost"] = sum(
                [
                    float(x["token_usage"].get("total_cost", 0))
                    for x in llm_costs
                    if x["monitoring_id"] == monitoring_id
                    and x["engine_name"] == engine_name
                ]
            )
        return llm_monitorings_costs
