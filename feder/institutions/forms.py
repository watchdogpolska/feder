# -*- coding: utf-8 -*-
from autocomplete_light import shortcuts as autocomplete_light
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin

from .models import Institution


class InstitutionForm(SingleButtonMixin, UserKwargModelFormMixin, autocomplete_light.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Institution
        fields = ['name', 'address', 'tags', 'jst']
        autocomplete_names = {'jst': 'JSTCommunityAutocomplete'}
