# -*- coding: utf-8 -*-
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Case


class CaseForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop('monitoring', None)
        super(CaseForm, self).__init__(*args, **kwargs)
        if self.monitoring:
            self.instance.monitoring = self.monitoring

    class Meta:
        model = Case
        fields = ['name', 'institution']
