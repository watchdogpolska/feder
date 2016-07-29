# -*- coding: utf-8 -*-
from atom.ext.guardian.forms import TranslatedUserObjectPermissionsForm
from atom.ext.crispy_forms.forms import SingleButtonMixin
from autocomplete_light import shortcuts as autocomplete_light
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Fieldset, Layout
from django import forms
from django.utils.translation import ugettext as _

from feder.letters.models import Letter

from .models import Monitoring


class MonitoringForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MonitoringForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Monitoring
        fields = ['name', 'description', 'notify_alert']


class CreateMonitoringForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    recipients = autocomplete_light.ModelMultipleChoiceField('InstitutionAutocomplete', label=_("Recipients"))
    text = forms.CharField(widget=forms.Textarea, label=_("Text"))

    def __init__(self, *args, **kwargs):
        super(CreateMonitoringForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(_("Monitoring"),
                     'name',
                     'description',
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
        fields = ['name', 'description']


class SelectUserForm(forms.Form):
    user = autocomplete_light.ModelChoiceField('UserAutocomplete', label=_("User"))


class SaveTranslatedUserObjectPermissionsForm(SingleButtonMixin,
                                              TranslatedUserObjectPermissionsForm):
    pass
