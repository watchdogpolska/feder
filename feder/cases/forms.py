# -*- coding: utf-8 -*-
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from dal import autocomplete
from django import forms

from .models import Case


class CaseForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop('monitoring', None)
        super(CaseForm, self).__init__(*args, **kwargs)
        self.instance.user = self.user
        if self.monitoring:
            self.instance.monitoring = self.monitoring

    class Meta:
        model = Case
        fields = ['name', 'institution']
        widgets = {
            'institution': autocomplete.ModelSelect2(
                url='institutions:autocomplete')
        }
