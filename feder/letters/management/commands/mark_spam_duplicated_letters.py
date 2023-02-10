from django.core.management.base import BaseCommand
from feder.letters.models import Letter


class Command(BaseCommand):
    help = "Mark duplicated letters as spam based on 'Message-ID'."

    def add_arguments(self, parser):
        # parser.add_argument(
        #     "--monitoring-pk", help="PK of monitoring which receive mail", required=True
        # )
        parser.add_argument(
            "--mark-spam", help="Mark duplicates as spam", action="store_true"
        )

    def handle(self, *args, **options):
        ids = set()
        print(options)
        for letter in (
            Letter.objects.all()
        ):
            print(f"Processing letter: {letter.pk}, ", end = "")
            if letter.message_id_header is None or letter.message_id_header == "":
                print("skipping due to missing 'Message-ID'.")
                continue
            if letter.message_id_header not in ids:
                print(
                    f"skipping due to unique 'Message-ID': {letter.message_id_header}"
                )
                ids.add(letter.message_id_header)
                continue
            print(
                f"to be marked as spam due to duplicated 'Message-ID': {letter.message_id_header}"
                )
            if options["mark_spam"]:
                letter.is_spam = Letter.SPAM.spam
                letter.save()