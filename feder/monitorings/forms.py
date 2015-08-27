# -*- coding: utf-8 -*-
from django import forms
from .models import Monitoring
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Layout, Fieldset
from django.utils.translation import ugettext as _
from autocomplete_light import ModelMultipleChoiceField
from atom.forms import SaveButtonMixin
from feder.letters.models import Letter


class MonitoringForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MonitoringForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Monitoring
        fields = ['name', 'description']


class CreateMonitoringForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    recipients = ModelMultipleChoiceField('InstitutionAutocomplete', label=_("Recipients"))
    text = forms.CharField(widget=forms.Textarea, label=_("Text"))

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
        count = 1
        for institution in self.cleaned_data['recipients']:
            postfix = " #%d" % (count, )
            Letter.send_new_case(user=self.user,
                                 monitoring=obj,
                                 postfix=postfix,
                                 institution=institution,
                                 text=text)
            count += 1
        return obj

    class Meta:
        model = Monitoring
        fields = ['name']
