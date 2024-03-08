import logging

from background_task import background
from django.utils.translation import gettext_lazy as _

from .models import LlmLetterRequest, LlmMonitoringRequest

logger = logging.getLogger(__name__)


@background(schedule=120)
def categorize_letter_in_background(letter_pk):
    from feder.letters.models import Letter

    letter = Letter.objects.filter(pk=letter_pk).first()

    if not letter:
        logger.warning(f"Letter with pk={letter_pk} not found.")
        return

    if not letter.is_incoming:
        logger.info(
            f"Letter (pk={letter_pk}) categorisation skipped - letter is not incoming."
        )
        return

    if letter.is_spam in [Letter.SPAM.spam, Letter.SPAM.probable_spam]:
        message = _("AI categorisation skipped for spam or probable spam.")
        logger.info(f"Letter (pk={letter_pk}): {message}")
        letter.ai_evaluation = message
        letter.save()
        return

    if letter.message_type in Letter.MESSAGE_TYPES_AUTO:
        message = _("AI categorisation skipped for auto reply letter.")
        logger.info(f"Letter (pk={letter_pk}): {message}")
        letter.ai_evaluation = message
        letter.save()
        return

    LlmLetterRequest.categorize_letter(letter)
    logger.info(f"Letter with pk={letter_pk} categorized.")
    if "A) email jest odpowiedzią" in letter.ai_evaluation:
        LlmLetterRequest.get_normalized_answers(letter)
        logger.info(f"Letter with pk={letter_pk} answer normalization processed.")
    else:
        logger.info(
            f"Letter with pk={letter_pk} is not a response - skipping normalization."
        )


@background(schedule=120)
def get_monitoring_normalized_response_template(monitoring_pk):
    from feder.monitorings.models import Monitoring

    monitoring = Monitoring.objects.filter(pk=monitoring_pk).first()

    if not monitoring:
        logger.warning(f"Monitoring with pk={monitoring_pk} not found.")
        return

    LlmMonitoringRequest.get_response_normalized_template(monitoring)
    logger.info(
        f"Monitoring (pk={monitoring_pk}) updated with normalized response template."
    )

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
        update_monitoring_responses_normalization(monitoring_pk)
        logger.info(
            f"Monitoring (pk={monitoring_pk}) tasks to normalize responses generated."
        )
        return
    else:
        logger.info(
            f"Monitoring (pk={monitoring_pk}) normalized response template not "
            + "changed - skipping normalization."
        )


@background(schedule=120)
def update_monitoring_responses_normalization(monitoring_pk):
    from feder.letters.models import Letter

    letters_to_normalize = (
        Letter.objects.all()
        .filter(record__case__monitoring__pk=monitoring_pk)
        .filter(author_user__isnull=True)
    )

    if not letters_to_normalize:
        logger.warning(
            f"No letters to normalize for monitoring with pk={monitoring_pk}."
        )
        return

    for letter in letters_to_normalize:
        categorize_letter_in_background(letter.pk)
