import email
import gzip
from datetime import datetime

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from feder.letters.models import Letter, LetterEmailDomain
from feder.main.utils import get_clean_email


class Command(BaseCommand):
    help = "Fill mail_from and mail_to addresses from eml and add mail domains."

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--monitoring-pk", help="PK of monitoring which receive mail",
    #         required=True
    #     )
    #     parser.add_argument(
    #         "--delete", help="Confirm deletion of email", action="store_true"
    #     )

    def handle(self, *args, **options):
        last_letter = Letter.objects.all().order_by("id").last().id
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Started {start_time}")
        for letter in Letter.objects.all().order_by("id"):
            print(f"Processing letter: {letter.pk} of {last_letter}")
            if not letter.eml or not default_storage.exists(letter.eml.path):
                print(f"Skipping {letter.pk} due to missing eml.")
                continue
            eml_content = letter.eml.file.read()
            if b"Subject:" not in eml_content:
                try:
                    content = gzip.decompress(eml_content)
                except Exception:
                    print(
                        f"Skipping {letter.pk} due to eml decompression error.",
                        f" {Exception}",
                    )
                    continue
            else:
                content = eml_content
            msg = email.message_from_bytes(content)
            # print(msg)
            letter.email_from = get_clean_email(msg["From"])
            is_outgoing = (
                letter.is_outgoing
                or "fedrowanie.siecobywatelska.pl" in letter.email_from
            )
            letter.email_to = get_clean_email(msg["To"])
            letter.message_id_header = msg["Message-ID"] or ""
            letter.save()
            print(
                f'email_from: {msg["From"]}, email_to: {msg["To"]},'
                f' msg Id: {msg["Message-ID"]}, is_outgoing: {is_outgoing}'
            )
            LetterEmailDomain.register_letter_email_domains(letter=letter)
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Completed {end_time}")
