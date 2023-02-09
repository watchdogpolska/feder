from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from feder.monitorings.models import Monitoring
from feder.letters.models import Letter, LetterEmailDomain
from io import BytesIO
import email
import gzip
from feder.main.utils import get_clean_email, get_email_domain


class Command(BaseCommand):
    help = "Fill mail_from and mail_to addresses from eml and add mail domains."

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--monitoring-pk", help="PK of monitoring which receive mail", required=True
    #     )
    #     parser.add_argument(
    #         "--delete", help="Confirm deletion of email", action="store_true"
    #     )

    def handle(self, *args, **options):
        last_letter = Letter.objects.all().order_by('id').last().id
        for letter in Letter.objects.all().order_by('id'):
            print(f"Processing letter: {letter.pk} of {last_letter}")
            if not letter.eml or not default_storage.exists(letter.eml.path):
                print(f"Skipping {letter.pk} due to missing eml.")
                continue
            eml_content = letter.eml.file.read()
            if b"Subject:" not in eml_content:
                try:
                    content = gzip.decompress(eml_content)
                except:
                    print(f"Skipping {letter.pk} due to eml decompression error.")
                    continue
            else:
                content = eml_content
            msg = email.message_from_bytes(content)
            # print(msg)
            print(f'email_from: {msg["From"]}, email_to: {msg["To"]}, msg Id: {msg["Message-ID"]}, is_outgoing: {is_outgoing}')
            letter.email_from = get_clean_email(msg['From'])
            is_outgoing = letter.is_outgoing or 'fedrowanie.siecobywatelska.pl' in letter.email_from
            letter.email_to = get_clean_email(msg['To'])
            letter.message_id_header = msg["Message-ID"] or ''
            letter.save()
            if get_email_domain(letter.email_from) != '':
                from_domain = get_email_domain(letter.email_from)
                if LetterEmailDomain.objects.filter(domain_name=from_domain).exists():
                    LetterEmailDomain.objects.get(domain_name=from_domain).add_email_from_letter()
                else:
                    letter_from_domain = LetterEmailDomain.objects.create(domain_name=from_domain)
                    letter_from_domain.add_email_from_letter()
            if get_email_domain(letter.email_to) != '':
                to_domain = get_email_domain(letter.email_to)
                if LetterEmailDomain.objects.filter(domain_name=to_domain).exists():
                    ledder_to_domain = LetterEmailDomain.objects.get(domain_name=to_domain)
                    letter_to_domain.add_email_to_letter()
                    if is_outgoing:
                        letter_to_domain.is_monitoring_email_to_domain = True
                        letter_to_domain.save()
                else:
                    letter_to_domain = LetterEmailDomain.objects.create(
                        domain_name=to_domain,
                        is_monitoring_email_to_domain = is_outgoing,
                    )
                    letter_to_domain.add_email_to_letter()
