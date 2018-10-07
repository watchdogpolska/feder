from __future__ import unicode_literals
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import filesizeformat

from feder.letters.models import Letter, Attachment


class Command(BaseCommand):
    help = "Scan unnecessary files in MEDIA_ROOT."

    NECCESSARY = {
        Letter: ['eml'],
        Attachment: ['attachment']
    }

    def add_arguments(self, parser):
        parser.add_argument('--size', action='store_true',
                            help="Calculate total size of unnecessary files")

    def handle(self, size, *args, **options):
        unnecessary = set()
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            unnecessary.update(os.path.join(root, file) for file in files)

        for model, fields in self.NECCESSARY.items():
            for field in fields:
                for obj in model.objects.exclude(**{field: ''}).iterator():
                    full_path = os.path.join(settings.MEDIA_ROOT,
                                             getattr(obj, field).name)
                    if full_path in unnecessary:
                        unnecessary.remove(full_path)

        for path in unnecessary:
            print(path)
        print("Found {} unnecessary files.".format(len(unnecessary)))

        if size:
            total_size = sum(os.path.getsize(path) for path in unnecessary)
            print("The unnecessary files have size of {} bytes in total.".format(
                filesizeformat(total_size)))
