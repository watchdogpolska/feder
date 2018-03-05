# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class ParcelsConfig(AppConfig):
    name = 'feder.parcels'

    def ready(self):
        from . import types
