import logging

from background_task import background

from .models import LlmLetterRequest

logger = logging.getLogger(__name__)


@background(schedule=120)
def categorize_letter_in_background(letter_pk):
    from feder.letters.models import Letter

    letter = Letter.objects.filter(pk=letter_pk).first()
    if (
        letter
        and letter.is_incoming
        and letter.is_spam not in [Letter.SPAM.spam, Letter.SPAM.probable_spam]
    ):
        LlmLetterRequest.categorize_letter(letter)
        logger.info(f"Letter with pk={letter_pk} categorized.")
    elif letter and not letter.is_incoming:
        logger.warning(
            f"Letter (pk={letter_pk}) categorisation skipped - letter is not incoming."
        )
    elif letter and letter.is_spam in [Letter.SPAM.spam, Letter.SPAM.probable_spam]:
        logger.warning(f"Letter (pk={letter_pk}) is spam, categorisation skipped.")
    else:
        logger.warning(f"Letter with pk={letter_pk} not found.")
