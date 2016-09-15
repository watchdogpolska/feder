# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible
from guardian.mixins import GuardianUserMixin


@python_2_unicode_compatible
class User(GuardianUserMixin, AbstractUser):

    def __str__(self):
        return self.username
