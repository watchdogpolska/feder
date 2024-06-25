import logging

from background_task import background
from django.utils.translation import gettext_lazy as _

from feder.llm_evaluation.prompts import EMAIL_IS_ANSWER, EMAIL_IS_SPAM

from .models import LlmLetterRequest, LlmMonitoringRequest

logger = logging.getLogger(__name__)


@background(schedule=120)
def categorize_letter_in_background(letter_pk):
    from feder.letters.models import Letter

    letter = Letter.objects.filter(pk=letter_pk).first()

    if not letter:
        msg = f"Letter with pk={letter_pk} not found."
        logger.warning(msg)
        return msg

    if not letter.is_incoming:
        msg = (
            f"Letter (pk={letter_pk}) categorisation skipped - letter is not incoming."
        )
        logger.info(msg)
        return msg

    if letter.is_spam in [Letter.SPAM.spam, Letter.SPAM.probable_spam]:
        message = _("AI categorisation skipped for spam or probable spam.")
        logger.info(f"Letter (pk={letter_pk}): {message}")
        letter.ai_evaluation = message
        letter.save()
        return f"Letter (pk={letter_pk}): {message}"

    if letter.message_type in Letter.MESSAGE_TYPES_AUTO:
        message = _("AI categorisation skipped for auto reply letter.")
        logger.info(f"Letter (pk={letter_pk}): {message}")
        letter.ai_evaluation = message
        letter.save()
        return f"Letter (pk={letter_pk}): {message}"

    the_same_content_evaluated = (
        Letter.objects.filter(
            title=letter.title,
            body=letter.body,
            ai_evaluation__isnull=False,
            ai_evaluation__icontains=EMAIL_IS_SPAM,
        )
        .exclude(pk=letter_pk)
        .first()
    )

    if the_same_content_evaluated:
        message = _(
            "AI categorisation skipped for letter with the same content "
            + "as already evaluated spam letter: "
        ) + str(the_same_content_evaluated.pk)
        logger.info(f"Letter (pk={letter_pk}): {message}")
        letter.ai_evaluation = the_same_content_evaluated.ai_evaluation
        letter.is_spam = the_same_content_evaluated.is_spam
        letter.save()
        letter_llm_request = LlmLetterRequest.objects.create(
            evaluated_letter=letter,
            engine_name="",
            request_prompt=message,
            status=LlmLetterRequest.STATUS.done,
            response=the_same_content_evaluated.ai_evaluation,
            token_usage={},
        )
        letter_llm_request.save()
        return f"Letter (pk={letter_pk}): {message}"

    LlmLetterRequest.categorize_letter(letter)
    logger.info(f"Letter with pk={letter_pk} categorized.")
    if EMAIL_IS_ANSWER in letter.ai_evaluation:
        LlmLetterRequest.get_normalized_answers(letter)
        logger.info(f"Letter with pk={letter_pk} answer normalization processed.")
        return f"Letter with pk={letter_pk} answer normalization processed."
    else:
        msg = (
            f"Letter with pk={letter_pk} is not a response - "
            + "skipping answers normalization."
        )
        logger.info(msg)
        return msg


@background(schedule=120)
def update_letter_normalized_answers(letter_pk):
    from feder.letters.models import Letter

    letter = Letter.objects.filter(pk=letter_pk).first()

    if not letter:
        msg = f"Letter with pk={letter_pk} not found."
        logger.warning(msg)
        return msg

    if letter.normalized_answer_is_up_to_date:
        msg = (
            f"Letter with pk={letter_pk} normalized answers are up to date - skipping."
        )
        logger.info(msg)
        return msg

    if not letter.ai_evaluation:
        categorize_letter_in_background(letter_pk)
        msg = (
            f"Letter with pk={letter_pk} has no AI evaluation. Task to update letter"
            + " categorization created."
        )
        logger.info(msg)
        return msg

    if EMAIL_IS_ANSWER in letter.ai_evaluation:
        LlmLetterRequest.get_normalized_answers(letter)
        msg = f"Letter with pk={letter_pk} answer normalization processed."
        logger.info(msg)
        return msg
    else:
        letter.normalized_response = None
        letter.save()
        msg = (
            f"Letter pk={letter_pk} is not a response - skipping answers normalization."
        )
        logger.info(msg)
        return msg


@background(schedule=120)
def categorize_letter_answer_to_monitoring_question(letter_pk, question_number):
    from feder.letters.models import Letter

    letter = Letter.objects.filter(pk=letter_pk).first()

    if not letter:
        msg = f"Letter with pk={letter_pk} not found."
        logger.warning(msg)
        return msg

    if EMAIL_IS_ANSWER in letter.ai_evaluation:
        LlmLetterRequest.categorize_answer(letter, question_number)
        msg = (
            f'Letter with pk={letter_pk} answer to question "{question_number}"'
            + " categorized."
        )
        logger.info(msg)
        return msg
    else:
        msg = (
            f"Letter with pk={letter_pk} is not a response - "
            + f'skipping question "{question_number}" categorization.'
        )
        logger.info(msg)
        return msg


@background(schedule=120)
def update_letter_answers_to_monitoring_questions_categorization(monitoring_pk):
    from feder.letters.models import Letter
    from feder.monitorings.models import Monitoring

    letters_to_categorize = (
        Letter.objects.all()
        .filter(record__case__monitoring__pk=monitoring_pk)
        .filter(author_user__isnull=True)
        .filter(ai_evaluation__contains=EMAIL_IS_ANSWER)
    )

    if not letters_to_categorize:
        msg = f"No letters to categorize answers for monitoring pk={monitoring_pk}."
        logger.warning(msg)
        return msg

    monitoring = Monitoring.objects.filter(pk=monitoring_pk).first()
    response_answers_categories_dict = (
        monitoring.get_normalized_response_answers_categories_dict()
    )
    questions_to_categorize_list = [
        k for k, v in response_answers_categories_dict.items() if v["answer_categories"]
    ]
    for letter in letters_to_categorize:
        for question_number in questions_to_categorize_list:
            categorize_letter_answer_to_monitoring_question(letter.pk, question_number)
    msg = (
        "Tasks to categorize Letters answers to monitoring questions "
        + f"generated for monitoring pk={monitoring_pk}."
    )
    return msg


@background(schedule=120)
def get_monitoring_normalized_response_template(monitoring_pk):
    from feder.monitorings.models import Monitoring

    monitoring = Monitoring.objects.filter(pk=monitoring_pk).first()

    if not monitoring:
        msg = f"Monitoring with pk={monitoring_pk} not found."
        logger.warning(msg)
        return msg

    LlmMonitoringRequest.get_response_normalized_template(monitoring)
    msg = f"Monitoring with pk={monitoring_pk} normalized response template generated."
    logger.info(msg)

    monitoring_llm_requests = (
        LlmMonitoringRequest.objects.filter(evaluated_monitoring=monitoring)
        .all()
        .order_by("-created")
    )

    # TODO: make sure to update when introducing more LlmMonitoringRequest methods
    # TODO: or find better solution
    if len(monitoring_llm_requests) == 1 or (
        len(monitoring_llm_requests) > 1
        and monitoring_llm_requests[0].response != monitoring_llm_requests[1].response
    ):
        update_monitoring_responses_categorization_and_normalization(monitoring_pk)
        msg += " Tasks to categorize and normalize responses generated."
        logger.info(msg)
        return msg
    else:
        msg += (
            " Template not changed - skipping responses categorization"
            + " and normalization."
        )
        logger.info(msg)
        return msg


@background(schedule=120)
def update_monitoring_responses_categorization_and_normalization(monitoring_pk):
    from feder.letters.models import Letter

    letters_to_normalize = (
        Letter.objects.all()
        .filter(record__case__monitoring__pk=monitoring_pk)
        .filter(author_user__isnull=True)
    )

    if not letters_to_normalize:
        msg = f"No letters to normalize for monitoring with pk={monitoring_pk}."
        logger.warning(msg)
        return msg

    for letter in letters_to_normalize:
        categorize_letter_in_background(letter.pk)

    msg = f"Tasks to categorize letters for monitoring pk={monitoring_pk} generated."
    return msg


@background(schedule=120)
def update_monitoring_responses_normalization(monitoring_pk):
    from feder.letters.models import Letter

    letters_to_normalize = (
        Letter.objects.all()
        .filter(record__case__monitoring__pk=monitoring_pk)
        .filter(author_user__isnull=True)
    )

    if not letters_to_normalize:
        msg = f"No letters to normalize for monitoring with pk={monitoring_pk}."
        logger.warning(msg)
        return msg

    for letter in letters_to_normalize:
        update_letter_normalized_answers(letter.pk)

    msg = f"Tasks to normalize letters for monitoring pk={monitoring_pk} generated."
    return msg
