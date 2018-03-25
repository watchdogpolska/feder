# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from guardian.mixins import GuardianUserMixin


@python_2_unicode_compatible
class User(GuardianUserMixin, AbstractUser):
    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
