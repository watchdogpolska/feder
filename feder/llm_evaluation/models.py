import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import TokenTextSplitter
from model_utils import Choices
from model_utils.models import TimeStampedModel

from .llm_tools import num_tokens_from_string
from .prompts import letter_categorization, letter_evaluation_intro


class LLmRequestQuerySet(models.QuerySet):
    def queued(self):
        return self.filter(status=self.model.STATUS.queued)


class LlmRequest(TimeStampedModel):
    STATUS = Choices(
        (0, "created", _("Created")),
        (1, "queued", _("Queued")),
        (2, "done", _("Done")),
        (3, "failed", _("Failed")),
    )
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
    token_usage = JSONField(
        verbose_name=_("LLM Engine token usage"), null=True, blank=True
    )
    objects = LLmRequestQuerySet.as_manager()

    class Meta:
        abstract = True


class LlmLetterRequest(LlmRequest):
    evaluated_letter = models.ForeignKey(
        "letters.Letter",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Evaluated Letter"),
    )

    @classmethod
    def categorize_letter(cls, letter):
        institution_name = ""
        monitoring_template = ""
        if letter.case and letter.case.monitoring:
            institution_name = letter.case.institution.name
            monitoring_template = letter.case.monitoring.template
        intro = letter_evaluation_intro.format(
            institution=institution_name,
            monitoring_question=monitoring_template,
        )
        test_prompt = letter_categorization.format(
            intro=intro,
            institution=institution_name,
            monitoring_response="",
        )
        q_tokens = num_tokens_from_string(
            test_prompt, settings.OPENAI_API_ENGINE.replace("so-", "")
        )
        # print(f"q_tokens: {q_tokens}")
        max_tokens = 8000 - q_tokens - 500
        # print(f"max_tokens: {max_tokens}")
        text_splitter = TokenTextSplitter(chunk_size=max_tokens, chunk_overlap=100)
        texts = text_splitter.split_text(letter.get_full_content())
        # print(
        #     "texts[0] tokens:",
        #     num_tokens_from_string(
        #         texts[0], settings.OPENAI_API_ENGINE.replace("so-", "")
        #     ),
        # )
        final_prompt = letter_categorization.format(
            intro=intro,
            institution=institution_name,
            monitoring_response=texts[0],
        )
        letter_llm_request = cls.objects.create(
            evaluated_letter=letter,
            engine_name=settings.OPENAI_API_ENGINE,
            request_prompt=final_prompt,
            status=cls.STATUS.created,
            response="",
            token_usage={},
        )
        letter_llm_request.save()
        model = ChatOpenAI(
            model_kwargs={
                "api_type": settings.OPENAI_API_TYPE,
                "api_key": settings.OPENAI_API_KEY,
                "api_version": settings.OPENAI_API_VERSION,
                "api_base": settings.OPENAI_API_BASE,
                "engine": settings.OPENAI_API_ENGINE,
            },
            temperature=settings.OPENAI_API_TEMPERATURE,
        )
        chain = letter_categorization | model | StrOutputParser()
        start_time = time.time()
        with get_openai_callback() as cb:
            resp = chain.invoke(
                {
                    "intro": intro,
                    "institution": institution_name,
                    "monitoring_response": texts[0],
                }
            )
        end_time = time.time()
        execution_time = end_time - start_time
        llm_info_dict = vars(cb)
        llm_info_dict["completion_time"] = execution_time
        letter_llm_request.response = resp
        letter_llm_request.token_usage = llm_info_dict
        letter_llm_request.status = cls.STATUS.done
        letter_llm_request.save()
        letter.ai_evaluation = resp
        letter.save()
        # print(f"resp: {resp}")
        # print(f"cb: {cb}")
        # print(f"execution_time: {execution_time}")


class LlmMonitoringRequest(LlmRequest):
    evaluated_monitoring = models.ForeignKey(
        "monitorings.Monitoring",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Evaluated Monitoring"),
    )
