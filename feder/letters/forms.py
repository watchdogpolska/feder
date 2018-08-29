# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from textwrap import wrap

from atom.ext.crispy_forms.forms import HelperMixin, SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms
from django.utils.translation import ugettext_lazy as _

from feder.cases.models import Case
from feder.letters.utils import get_body_with_footer
from feder.records.models import Record
from .models import Letter
from feder.letters.signals import MessageParser

QUOTE_TPL = "W nawiązaniu do pisma z dnia {created} z adresu {email}:\n{quoted}"


class LetterForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    case = forms.ModelChoiceField(queryset=Case.objects.all(), label=_("Case"),
                                  widget=autocomplete.ModelSelect2(url='cases:autocomplete-find'))

    def __init__(self, *args, **kwargs):
        case = kwargs.pop('case', None)
        super(LetterForm, self).__init__(*args, **kwargs)
        self.initial['case'] = case or kwargs.get('instance').case
        self.helper.form_tag = False

    class Meta:
        model = Letter
        fields = ['title', 'body', 'case', 'note', ]

    def save(self, *args, **kwargs):
        self.instance.record.case = self.cleaned_data['case']
        self.instance.record.save()

        return super(LetterForm, self).save(*args, **kwargs)


class ReplyForm(HelperMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop('letter')
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.user_can_reply = self.user.has_perm('reply', self.letter.case.monitoring)
        self.user_can_save = self.user.has_perm('add_draft', self.letter.case.monitoring)

        self.set_dynamic_field_initial()
        self.add_form_buttons()

    def set_dynamic_field_initial(self):
        self.fields['title'].initial = "Re: {title}".format(title=self.letter.title)
        self.fields['body'].initial = get_body_with_footer("", self.letter.case.monitoring.email_footer)
        self.fields['quote'].initial = self.get_quote()

    def add_form_buttons(self):
        if self.user_can_reply and self.user_can_save:
            self.helper.add_input(Submit('save', _("Save draft"), css_class="btn-default"))
            self.helper.add_input(Submit('send', _("Send reply"), css_class="btn-primary"))
        elif self.user_can_save:
            self.helper.add_input(Submit('save', _("Save draft"), css_class="btn-primary"))
        elif self.user_can_reply:
            self.helper.add_input(Submit('send', _("Send reply"), css_class="btn-primary"))

    def clean(self):
        if not (self.user_can_reply or self.user_can_save):
            raise forms.ValidationError(_(
                "Nothing to do. You do not have permission to save draft or send replies."
            ))
        if not self.user_can_reply and 'send' in self.data:
            raise forms.ValidationError(_(
                "You do not have permission to send replies."
            ))
        if not self.user_can_save and 'save' in self.data:
            raise forms.ValidationError(_(
                "You do not have permission to save draft."
            ))
        return super(ReplyForm, self).clean()

    def get_quote(self):
        quoted = "> " + "\n> ".join(wrap(self.letter.body, width=80))
        return QUOTE_TPL.format(quoted=quoted, **self.letter.__dict__)

    def save(self, *args, **kwargs):
        self.instance.author_user = self.user
        if not hasattr(self.instance, 'record'):
            self.instance.record = Record.objects.create(case=self.letter.case)
        obj = super(ReplyForm, self).save(*args, **kwargs)
        return obj

    class Meta:
        model = Letter
        fields = ['title', 'body', 'quote']


class AssignMessageForm(SingleButtonMixin, forms.Form):
    action_text = _("Assign")
    case = forms.ModelChoiceField(queryset=Case.objects.all(), label=_("Case number"),
                                  widget=autocomplete.ModelSelect2(url='cases:autocomplete-find'))

    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop('message')
        super(AssignMessageForm, self).__init__(*args, **kwargs)

    def save(self):
        return MessageParser(message=self.message, case=self.cleaned_data['case']).insert()


class AssignLetterForm(SingleButtonMixin, forms.Form):
    action_text = _("Assign")
    case = forms.ModelChoiceField(queryset=Case.objects.all(), label=_("Case number"),
                                  widget=autocomplete.ModelSelect2(url='cases:autocomplete-find'))

    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop('letter')
        super(AssignLetterForm, self).__init__(*args, **kwargs)

    def save(self):
        self.letter.case = self.cleaned_data['case']
        self.letter.record.save()
        self.letter.case.save()


class ReassignLetterForm(SingleButtonMixin, forms.ModelForm):
    action_text = _("Reassign")

    case = forms.ModelChoiceField(queryset=Case.objects.all(), label=_("Case number"),
                                  widget=autocomplete.ModelSelect2(url='cases:autocomplete-find'))

    def save(self, commit=True):
        self.instance.case = self.cleaned_data['case']
        self.instance.record.save()
        return super(ReassignLetterForm, self).save(commit)
