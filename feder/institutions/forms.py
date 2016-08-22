# -*- coding: utf-8 -*-
from dal import autocomplete
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin

from .models import Institution


class InstitutionForm(SingleButtonMixin, UserKwargModelFormMixin):
    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Institution
        fields = ['name', 'address', 'tags', 'jst']
        widgets = {
            'jst': autocomplete.ModelSelect2(url='country-autocomplete')
        }
