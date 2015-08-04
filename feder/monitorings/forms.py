# -*- coding: utf-8 -*-
from django import forms
from .models import Monitoring
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Layout, Fieldset
from django.utils.translation import ugettext as _
from atom.forms import SaveButtonMixin
from feder.letter.models import Letter
from feder.institutions.models import Institution


class MonitoringForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MonitoringForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Monitoring
        fields = ['name']


class CreateMonitoringForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(queryset=Institution.objects.all())
    text = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(CreateMonitoringForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(_("Monitoring"),
                'name',
                     ),
            Fieldset(_("Content of new letter"),
                'recipients',
                'text'
                     )
            )

    def save(self, *args, **kwargs):
        self.instance.user = self.user
        obj = super(CreateMonitoringForm, self).save(*args, **kwargs)
        text = self.cleaned_data['text']
        for institution in self.cleaned_data['recipients']:
            Letter.send_new_case(user=self.user, monitoring=obj, institution=institution, text=text)
        return obj

    class Meta:
        model = Monitoring
        fields = ['name']
