import logging

from background_task import background

logger = logging.getLogger(__name__)


@background(schedule=120)
def update_letter_attachments_text_content(letter_pk):
    from feder.letters.models import Letter

    letter = Letter.objects.filter(pk=letter_pk).first()

    if not letter:
        msg = f"Letter with pk={letter_pk} not found."
        logger.warning(msg)
        return msg

    letter_attachments = letter.attachment_set.all()
    msg = (
        f"Letter {letter_pk} - attachments to update text content: "
        + f"{letter_attachments.count()}"
    )
    logger.info(msg)
    for attachment in letter_attachments:
        attachment.update_text_content()
        msg += f"\nAttachment {attachment.pk} text content updated."
        logger.info(f"Letter {letter_pk} - attachment pk={attachment.pk} updated.")
    logger.info(f"Letter {letter_pk} - attachments text content updated.")
    return msg
