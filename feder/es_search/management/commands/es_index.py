from django.core.management.base import BaseCommand

from ....letters.models import Letter
from ...tasks import index_letter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("monitoring_ids", nargs="*", type=int)
        parser.add_argument("--skip-queue", action="store_true")

    def handle(self, *args, **options):
        qs = Letter.objects.all().exclude_spam()
        if options["monitoring_ids"]:
            qs = qs.filter(record__case__monitoring__in=options["monitoring_ids"])
        for letter_id in qs.values_list("id", flat=True).iterator():
            ids = [letter_id]
            if options["skip_queue"]:
                index_letter.now(ids)
            else:
                index_letter(ids)
            self.stdout.write(f"Add letter of #{letter_id}\n")
