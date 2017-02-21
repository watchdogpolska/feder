# -*- coding: utf-8 -*-
from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms
from django.utils.translation import ugettext as _

from .models import Question, Questionary
from .utils import get_modulators


class QuestionaryForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

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


class QuestionForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        questionary = kwargs.pop('questionary')
        super(QuestionForm, self).__init__(*args, **kwargs)
        choices = [(key, mod.description) for key, mod in get_modulators().items()]
        self.fields['genre'] = forms.ChoiceField(choices=choices, label=_("Genre"))
        self.instance.questionary = questionary

    class Meta:
        model = Question
        fields = ['position', 'genre']


class QuestionDefinitionForm(SingleButtonMixin, UserKwargModelFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        kwargs['initial'] = self.instance.definition
        super(QuestionDefinitionForm, self).__init__(*args, **kwargs)
        self.construct_form()

    def construct_form(self):
        for name, field in self.instance.modulator.list_create_question_fields():
            self.fields[name] = field

    def save(self):
        self.instance.definition = self.cleaned_data
        self.instance.save()
        return self.instance
