import itertools

from django.core.management.base import BaseCommand
from ...tasks import index_letter
from ....letters.models import Letter


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("monitoring_ids", nargs="*", type=int)
        parser.add_argument("--chunk", type=int, default=50)
        parser.add_argument("--skip-queue", action="store_true")

    def handle(self, *args, **options):
        qs = Letter.objects.all()
        if options["monitoring_ids"]:
            qs = qs.filter(
                letter__record__case__monitoring__in=options["monitoring_ids"]
            )
        for chunk in split_seq(
            qs.values_list("id", flat=True).iterator(), options["chunk"]
        ):
            ids = chunk
            if options["skip_queue"]:
                index_letter.now(ids)
            else:
                index_letter(ids)
            self.stdout.write("Add chunk from {} to {}\n".format(min(ids), max(ids)))
        self.stdout.write("Add chunk from {} to {}\n".format(min(ids), max(ids)))
