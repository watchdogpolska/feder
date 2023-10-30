import logging

from django.core.management.base import BaseCommand

from feder.letters.logs.models import LogRecord
from feder.letters.logs.utils import get_emaillabs_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update the status of sent letters based on the Emaillabs API"

    def handle(self, *args, **options):
        client = get_emaillabs_client()
        skipped, saved = LogRecord.objects.parse_rows(client.get_emails_iter())
        logger.info(f"Saved {saved} new logs record and skipped {skipped} records.")
