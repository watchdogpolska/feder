from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TaskConfig(AppConfig):
    name = "feder.tasks"
    verbose_name = _("Tasks")

    def ready(self):
        from .signals import *  # noqa
