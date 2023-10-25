import logging

from background_task import background

from .models import LlmLetterRequest

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
        message = f"AI categorisation skipped for spam or probable spam."
        logger.info(f"Letter (pk={letter_pk}): {message}")
        letter.ai_evaluation = message
        letter.save()
        return

    LlmLetterRequest.categorize_letter(letter)
    logger.info(f"Letter with pk={letter_pk} categorized.")