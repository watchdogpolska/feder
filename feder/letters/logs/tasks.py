import logging

from background_task import background

logger = logging.getLogger(__name__)


@background(schedule=120)
def update_sent_letter_status():
    """
    Update the status of sent letters using Emaillabs API
    """
    from feder.letters.logs.models import LogRecord
    from feder.letters.logs.utils import get_emaillabs_client

    client = get_emaillabs_client()
    skipped, saved = LogRecord.objects.parse_rows(client.get_emails_iter())
    logger.info(f"Saved {saved} new logs record and skipped {skipped} records.")
