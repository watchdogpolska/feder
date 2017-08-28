# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel

from django.conf import settings

from django.utils.translation import ugettext_lazy as _


class LightUserQuerySet(models.QuerySet):
    pass


@python_2_unicode_compatible
class LightUser(TimeStampedModel):
    ip = models.GenericIPAddressField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    objects = LightUserQuerySet.as_manager()

    class Meta:
        verbose_name = _("Light User")
        verbose_name_plural = _("Light Users")

    def __str__(self):
        if self.user_id:
            return "LH-{} (User ID: {})".format(self.ip, self.user_id)
        return "LH-{} ({})".format(self.ip, self.created.date())
