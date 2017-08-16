# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LightUserConfig(AppConfig):
    name = 'feder.light_user'
    verbose_name = _("Light Users")

    def ready(self):
        from .signals import *  # noqa
