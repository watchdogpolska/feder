# -*- coding: utf-8 -*-
from django import forms
from .models import Case
from braces.forms import UserKwargModelFormMixin
from atom.forms import SaveButtonMixin
import autocomplete_light


class CaseForm(SaveButtonMixin, UserKwargModelFormMixin, autocomplete_light.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CaseForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Case
        fields = ['name', 'monitoring', 'institution']
