# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class RecordsConfig(AppConfig):
    name = "feder.records"

    def ready(self):
        from . import checks
