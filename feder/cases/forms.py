# -*- coding: utf-8 -*-
from django import forms
from .models import Case
from braces.forms import UserKwargModelFormMixin


class CaseForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CaseForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Case
        fields = ['name', 'monitoring', 'institution']
