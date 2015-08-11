# -*- coding: utf-8 -*-
from django import forms
from atom.forms import SaveButtonMixin, HelperMixin
from braces.forms import UserKwargModelFormMixin
from .models import Questionary, Question
from .modulator import modulators


class QuestionaryForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionaryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Questionary
        fields = ['title', 'monitoring', ]


class BoolQuestionForm(HelperMixin, forms.Form):
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
        self.fields['genre'] = forms.ChoiceField(choices=choices)
        self.instance.questionary = questionary

    def save(self, blob, *args, **kwargs):
        self.instance.blob = blob
        return super(QuestionForm, self).save(*args, **kwargs)

    class Meta:
        model = Question
        fields = ['position', 'genre']
