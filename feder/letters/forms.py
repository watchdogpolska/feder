# -*- coding: utf-8 -*-
from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Letter


class LetterForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        case = kwargs.pop('case', None)
        super(LetterForm, self).__init__(*args, **kwargs)
        if case:
            self.instance.case = case

    class Meta:
        model = Letter
        fields = ['title', 'body']
