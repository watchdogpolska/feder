from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from feder.monitorings.models import Monitoring
from feder.letters.models import Letter, LetterEmailDomain
from io import BytesIO
import email
import gzip

def get_clean_email(email):
    if '<' in email:
        email = email.split('<')[1]
    if '>' in email:
        email = email.split('>')[0]
    return email

class Command(BaseCommand):
    help = "Fill mail_from and mail_to addresses from eml."

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--monitoring-pk", help="PK of monitoring which receive mail", required=True
    #     )
    #     parser.add_argument(
    #         "--delete", help="Confirm deletion of email", action="store_true"
    #     )

    def handle(self, *args, **options):
        from_domains = {}
        for letter in Letter.objects.all().order_by('id'):
            print(f"Processing letter: {letter.pk}")
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
            print(f'email_from: {msg["From"]}, email_to: {msg["To"]}, msg Id: {msg["Message-ID"]}')
            letter.email_from = get_clean_email(str(msg['From']))[-99:]
            if ',' in str(msg['To']):
                letter.email_to = get_clean_email(str(msg['To']).split(',')[0])
            else:
                letter.email_to = get_clean_email(str(msg['To']))[-99:]
            letter.message_id_header = msg["Message-ID"] or ''
            letter.save()
            if '@' in letter.email_from:
                from_domain = letter.email_from.split('@')[1]
                if LetterEmailDomain.objects.filter(domain_name=from_domain).exists():
                    LetterEmailDomain.objects.get(domain_name=from_domain).add_email_from_letter()
                else:
                    letter_from_domain = LetterEmailDomain.objects.create(domain_name=from_domain)
                    letter_from_domain.add_email_from_letter()
            if '@' in letter.email_to:
                to_domain = letter.email_to.split('@')[1]
                if LetterEmailDomain.objects.filter(domain_name=to_domain).exists():
                    LetterEmailDomain.objects.get(domain_name=to_domain).add_email_to_letter()
                else:
                    letter_to_domain = LetterEmailDomain.objects.create(domain_name=to_domain)
                    letter_to_domain.add_email_to_letter()
