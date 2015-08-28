# -*- coding: utf-8 -*-
from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Letter


class LetterForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LetterForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Letter
        fields = ['title', 'body']
