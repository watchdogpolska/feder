from __future__ import unicode_literals
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import filesizeformat


class Command(BaseCommand):
    help = "Scan unnecessary files in MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument('--size', action='store_true',
                            help="Calculate total size of unnecessary files")

    def handle(self, size, *args, **options):
        available = set()
        required = set()

        available.update(
            os.path.join(root, filename).decode('utf-8')
            for root, dirs, files in os.walk(settings.MEDIA_ROOT)
            for filename in files
        )

        required.update(
            os.path.join(settings.MEDIA_ROOT, getattr(obj, field).name)
            for model_str, params in settings.NECCESSARY_FILES.items()
            for field in params['fields']
            for obj in apps
                .get_model(model_str)
                .objects
                .exclude(**{field: ''})
                .iterator()
        )

        unnecessary = available - required
        missing = required - available

        for path in unnecessary:
            self.stdout.write(path)
        self.stdout.write(
            "Found {} unnecessary files.".
                format(len(unnecessary)).encode('utf-8')
        )
        self.stdout.write(
            "Found {} missing files.".
                format(len(missing)).encode('utf-8')
        )

        if not size:
            return
        total_size = sum(os.path.getsize(path) for path in unnecessary)
        self.stdout.write(
            "The unnecessary files have size of {} bytes in total.".
                format(filesizeformat(total_size))
        )
