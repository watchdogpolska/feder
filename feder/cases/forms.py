# -*- coding: utf-8 -*-
import autocomplete_light
from braces.forms import UserKwargModelFormMixin

from atom.forms import SaveButtonMixin

from .models import Case


class CaseForm(SaveButtonMixin, UserKwargModelFormMixin, autocomplete_light.ModelForm):
    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop('monitoring', None)
        super(CaseForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.monitoring:
            self.instance.monitoring = self.monitoring
        super(CaseForm, self).save(*args, **kwargs)

    class Meta:
        model = Case
        fields = ['name', 'institution']
