import logging

from background_task import background
from django.conf import settings

logger = logging.getLogger(__name__)


@background(schedule=600, remove_existing_tasks=True)
def update_sent_letter_status():
    """
    Update the status of sent letters using Emaillabs API
    """
    if settings.APP_MODE == "DEV":
        msg = "Skipping update_sent_letter_status task in DEV mode."
        logger.info(msg)
        return msg

    from feder.letters.logs.models import LogRecord
    from feder.letters.logs.utils import get_emaillabs_client

    client = get_emaillabs_client()
    skipped, saved = LogRecord.objects.parse_rows(client.get_emails_iter())
    msg = f"Saved {saved} new logs record and skipped {skipped} records."
    logger.info(msg)
    return msg
