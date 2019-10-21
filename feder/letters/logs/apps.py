# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LogsConfig(AppConfig):
    name = "feder.letters.logs"
    verbose_name = _("Logs of letter")

    def ready(self):
        from . import checks
