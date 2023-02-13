from django.core.management.base import BaseCommand
from feder.letters.models import Letter
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
        letter_id_headers = Letter.objects.values_list("message_id_header", flat=True)
        letter_id_headers_counter = Counter(letter_id_headers)
        letter_id_headers_counter_info = {}
        for k, v in letter_id_headers_counter.items():
            if v > 1 and k != "":
                c = set(
                    Letter.objects.filter(message_id_header=k).values_list(
                        "record__case__name", flat=True
                    )
                )
                m = set(
                    Letter.objects.filter(message_id_header=k).values_list(
                        "record__case__monitoring__name", flat=True
                    )
                )
                letter_id_headers_counter_info[k] = {
                    "count": v,
                    "case": c,
                    "monitoring": m,
                }
                print(k, letter_id_headers_counter_info[k])
