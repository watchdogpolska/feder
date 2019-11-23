from django.core.management.base import BaseCommand
from tqdm import tqdm

from feder.records.models import Record, AbstractRecord


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--fix", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--no-progress", dest="progress", action="store_false")

    def handle(self, *args, **options):

        my_iter = tqdm if options["progress"] else lambda x, *args, **kwargs: x

        for record in my_iter(Record.objects.all()):
            if record.content_object:
                continue
            self.stdout.write(
                self.style.ERROR("Invalid record (pk={})".format(record.pk))
            )
            if options["fix"]:
                self.stderr.write(
                    self.style.SUCCESS("Removed record (pk={})".format(record.pk))
                )
            if options["fix"] and not options["dry_run"]:
                record.delete()

        related_models = [
            field.related_model
            for field in Record._meta.related_objects
            if issubclass(field.related_model, AbstractRecord)
        ]
        for related_model in my_iter(related_models):
            verbose_name = related_model._meta.verbose_name
            for obj in my_iter(related_model.objects.all(), desc=verbose_name):
                if obj.record:
                    continue
                msg = "Invalid {} (pk={}, record={})".format(
                    verbose_name, obj.pk, repr(obj.record)
                )
                self.stdout.write(self.style.ERROR(msg))
