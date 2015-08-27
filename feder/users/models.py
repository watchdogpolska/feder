# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import AbstractUser


# from django.db import models
# from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    def __unicode__(self):
        return self.username
