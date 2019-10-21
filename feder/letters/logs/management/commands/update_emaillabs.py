from django.core.management.base import BaseCommand

from feder.letters.logs.models import LogRecord
from feder.letters.logs.utils import get_emaillabs_client


class Command(BaseCommand):
    help = "Update the status of sent letters based on the Emaillabs API"

    def handle(self, *args, **options):
        client = get_emaillabs_client()
        skipped, saved = LogRecord.objects.parse_rows(client.get_emails_iter())
        self.stdout.write(
            "Saved {} new logs record and skipped {} records.".format(saved, skipped)
        )
