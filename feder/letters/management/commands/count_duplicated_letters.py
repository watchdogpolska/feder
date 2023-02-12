from django.core.management.base import BaseCommand
from feder.letters.models import Letter
from feder.monitorings.models import Monitoring
from collections import Counter


class Command(BaseCommand):
    help = "Count duplicated letters based on 'Message-ID'."

    # def add_arguments(self, parser):
        # parser.add_argument(
        #     "--monitoring-pk", help="PK of monitoring which receive mail",
        #      required=True
        # )
        # parser.add_argument(
        #     "--mark-spam", help="Mark duplicates as spam", action="store_true"
        # )
        # parser.add_argument(
        #     "--delete", help="Delete duplicate letters", action="store_true"
        # )

    def handle(self, *args, **options):
        letter_id_headers = Letter.objects.values_list(
            'message_id_header', flat=True
        )
        letter_id_headers_counter = Counter(letter_id_headers)
        letter_id_headers_counter_info = {}
        for (k,v) in letter_id_headers_counter.items():
            if v > 1 and k != "":
                c = set(Letter.objects.filter(message_id_header=k).values_list("record__case__name",flat=True))
                m = set(Letter.objects.filter(message_id_header=k).values_list("record__case__monitoring__name", flat=True))
                letter_id_headers_counter_info[k] = {
                    "count": v, 
                    "case": c,
                    "monitoring": m,
                }
                print(k, letter_id_headers_counter_info[k])
    
        # ids = set()
        # print(options)
        # for letter in Letter.objects.all():
        #     print(f"Processing letter: {letter.pk}, ", end="")
        #     if letter.message_id_header is None or letter.message_id_header == "":
        #         print("skipping due to missing 'Message-ID'.")
        #         continue
        #     if letter.message_id_header not in ids:
        #         print(
        #             f"skipping due to unique 'Message-ID': {letter.message_id_header}"
        #         )
        #         ids.add(letter.message_id_header)
        #         continue
        #     print(
        #         f"to be marked as spam due to duplicated "
        #         f"'Message-ID': {letter.message_id_header}"
        #     )
        #     if options["mark_spam"]:
        #         letter.is_spam = Letter.SPAM.spam
        #         letter.save()
        #     elif options["delete"]:
        #         letter.delete()
        #     else:



