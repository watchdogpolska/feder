# -*- coding: utf-8 -*-
from atom.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
import autocomplete_light
from .models import Institution


class InstitutionForm(SingleButtonMixin, UserKwargModelFormMixin, autocomplete_light.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Institution
        fields = ['name', 'address', 'tags', 'jst']
        autocomplete_names = {'jst': 'JednostkaAdministracyjnaCommunityAutocomplete'}
