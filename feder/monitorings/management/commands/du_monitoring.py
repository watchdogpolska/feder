from __future__ import unicode_literals
import os

from django.apps import apps
from django.core.management.base import BaseCommand

from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import force_text

from feder.monitorings.models import Monitoring


def safe_stat(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


class Command(BaseCommand):
    help = "Commands to calculate total usage of disk by files per monitoring."

    def add_arguments(self, parser):
        parser.add_argument('monitorings', nargs='?')

    def handle(self, monitorings, *args, **options):
        qs_filter = {'pk__in': monitorings} if monitorings else {}

        for monitoring in Monitoring.objects.filter(**qs_filter).all():
            size = sum(
                safe_stat(
                    os.path.join(
                        settings.MEDIA_ROOT,
                        getattr(obj, field).name
                    )
                )
                for model_str, params in settings.NECCESSARY_FILES.items()
                for field in params['fields']
                for obj in apps
                .get_model(model_str)
                .objects
                .filter(**{params['path']: monitoring})
                .exclude(**{field: ''})
                .iterator()
            )
            self.stdout.write(
                "{} => {}".format(force_text(monitoring), filesizeformat(size))
            )
