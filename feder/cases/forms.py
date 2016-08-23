# -*- coding: utf-8 -*-
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin

from .models import Case


class CaseForm(SingleButtonMixin, UserKwargModelFormMixin):

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
