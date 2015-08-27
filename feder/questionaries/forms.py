# -*- coding: utf-8 -*-
from atom.forms import HelperMixin, SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms
from django.utils.translation import ugettext as _

from .models import Question, Questionary
from .modulator import modulators


class QuestionaryForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop('monitoring', None)
        super(QuestionaryForm, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            del self.fields['lock']

    def save(self, *args, **kwargs):
        if self.monitoring:
            self.instance.monitoring = self.monitoring
        return super(QuestionaryForm, self).save(*args, **kwargs)

    class Meta:
        model = Questionary
        fields = ['title', 'lock']


class BoolQuestionForm(HelperMixin, UserKwargModelFormMixin, forms.Form):
    def __init__(self, genre, *args, **kwargs):
        self.genre = genre
        super(BoolQuestionForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        modulators[genre]().create(self.fields)


class QuestionForm(HelperMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        questionary = kwargs.pop('questionary')
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        choices = [(key, mod.description) for key, mod in modulators.items()]
        self.fields['genre'] = forms.ChoiceField(choices=choices, label=_("Genre"))
        self.instance.questionary = questionary

    def save(self, blob, *args, **kwargs):
        self.instance.blob = blob
        return super(QuestionForm, self).save(*args, **kwargs)

    class Meta:
        model = Question
        fields = ['position', 'genre']
