# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms

from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name")
