# -*- coding: utf-8 -*-
from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Alert


class AlertForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop('monitoring', None)
        super(AlertForm, self).__init__(*args, **kwargs)
        if not self.instance.pk and not self.user.is_anonymous():
            self.instance.author = self.user
        if self.monitoring:
            self.instance.monitoring = self.monitoring

    class Meta:
        model = Alert
        fields = ['reason', ]
