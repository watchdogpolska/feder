# -*- coding: utf-8 -*-
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Letter


class LetterForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LetterForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Letter
        fields = ['title', 'body']
