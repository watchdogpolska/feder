# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from textwrap import wrap

from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Letter

QUOTE_TPL = "W nawiązaniu do pisma z dnia {created} z adresu {email}:\n{quoted}"


class LetterForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        case = kwargs.pop('case', None)
        super(LetterForm, self).__init__(*args, **kwargs)
        if case:
            self.instance.case = case

    class Meta:
        model = Letter
        fields = ['title', 'body']


class ReplyForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop('letter', None)
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = "Re: {title}".format(title=self.letter.title)
        self.fields['quote'].initial = self.get_quote()
        if self.letter:
            self.instance.author_user = self.user
            self.instance.case = self.letter.case

    def get_quote(self):
        quoted = "> " + "\n> ".join(wrap(self.letter.body, width=80))
        return QUOTE_TPL.format(quoted=quoted, **self.letter.__dict__)

    def save(self):
        obj = super(ReplyForm, self).save()
        self.instance.send()
        return obj

    class Meta:
        model = Letter
        fields = ['title', 'body', 'quote']
