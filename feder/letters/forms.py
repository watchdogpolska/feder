# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from textwrap import wrap

from atom.ext.crispy_forms.forms import HelperMixin, SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Letter

QUOTE_TPL = "W nawiązaniu do pisma z dnia {created} z adresu {email}:\n{quoted}"


class LetterForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        case = kwargs.pop('case', None)
        super(LetterForm, self).__init__(*args, **kwargs)
        if case:
            self.instance.case = case

    class Meta:
        model = Letter
        fields = ['title', 'body', 'note']


class ReplyForm(HelperMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop('letter', None)
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.user_can_reply = self.user.has_perm('reply', self.letter.case.monitoring)
        self.user_can_save = self.user.has_perm('add_draft', self.letter.case.monitoring)

        self.set_dynamic_field_initial()
        self.add_form_buttons()

    def set_dynamic_field_initial(self):
        if self.letter:
            self.fields['title'].initial = "Re: {title}".format(title=self.letter.title)
            self.fields['quote'].initial = self.get_quote()
            self.instance.author_user = self.user
            self.instance.case = self.letter.case

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
        obj = super(ReplyForm, self).save(*args, **kwargs)
        if 'send' in self.data:
            self.instance.send()
        return obj

    class Meta:
        model = Letter
        fields = ['title', 'body', 'quote']
