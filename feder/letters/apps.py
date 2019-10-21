from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LetterConfig(AppConfig):
    name = "feder.letters"
    verbose_name = _("Letter")

    def ready(self):
        from . import signals
        from . import types

        super(LetterConfig, self).ready()
