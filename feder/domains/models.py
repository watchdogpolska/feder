# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from model_utils.models import TimeStampedModel
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Domain(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    active = models.BooleanField(default=True, help_text=_("Activity status"))

    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
        ordering = ["created"]

    def __str__(self):
        return self.name
