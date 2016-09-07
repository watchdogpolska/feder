# -*- coding: utf-8 -*-
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from dal import autocomplete
from django import forms

from .models import Institution


class InstitutionForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Institution
        fields = ['name', 'tags', 'jst']
        widgets = {
            'jst': autocomplete.ModelSelect2(url='teryt:community-autocomplete')
        }
