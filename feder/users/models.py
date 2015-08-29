# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible


# from django.db import models
# from django.utils.translation import ugettext_lazy as _

@python_2_unicode_compatible
class User(AbstractUser):

    def __str__(self):
        return self.username
