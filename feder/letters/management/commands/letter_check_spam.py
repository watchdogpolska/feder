from django.core.management.base import BaseCommand
from feder.letters.models import Letter, LetterEmailDomain
from feder.main.utils import get_email_domain



class Command(BaseCommand):
    help = "Remove duplicated incoming letters based on 'Message-ID'."

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--monitoring-pk", help="PK of monitoring which receive mail", required=True
    #     )
    #     parser.add_argument(
    #         "--delete", help="Confirm deletion of email", action="store_true"
    #     )

    def handle(self, *args, **options):
        letter_count = 0
        spam_count = 0
        for letter in (
            Letter.objects.is_incoming().all()
        ):
            if letter.email_from is not None and "@" in letter.email_from:
                from_domain = LetterEmailDomain.objects.filter(
                    domain_name=get_email_domain(letter.email_from)
                ).first()
            else:
                from_domain = None
            letter_count += 1
            print(f"Processing letter: {letter.pk}, ", end = "")
            letter.spam_check()
            if letter.is_spam == Letter.SPAM.probable_spam:
                spam_count += 1
                print(f"probable spam")
            else:
                print("")
        print(f'letters: {letter_count}; spam: {spam_count}')
