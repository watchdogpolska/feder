# -*- coding: utf-8 -*-
from django import forms
from .models import Questionary, Question
from atom.forms import SaveButtonMixin, HelperMixin
from braces.forms import UserKwargModelFormMixin
from django.utils.functional import cached_property
from .modulator import modulators


class QuestionaryForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionaryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Questionary
        fields = ['title', 'monitoring', ]


class AnswerForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        self.question = question
        super(AnswerForm, self).__init__(*args, **kwargs)
        modulator = modulators[question.genre](question.blob)
        modulator.answer(self.fields)


class AnswerFormSet(object):  # How use django formsets?
    def __init__(self, questionary, *args, **kwargs):
        self.questionary = questionary
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.as_table()

    def __iter__(self):
        """Yields the forms in the order they should be rendered"""
        return iter(self.forms)

    def __getitem__(self, index):
        """Returns the form at the given index, based on the rendering order"""
        return self.forms[index]

    def __len__(self):
        return len(self.forms)

    @cached_property
    def forms(self):
        """
        Instantiate forms at first property access.
        """
        # DoS protection is included in total_form_count()
        forms = [AnswerForm(question=question, prefix=str(question.pk), *self.args, **self.kwargs)
            for question in self.questionary.question_set.all()]
        return forms

    def is_valid(self):
        """
        Returns True if every form in self.forms is valid.
        """
        if not self.is_bound:
            return False
        forms_valid = True

        for form in self.forms:
            forms_valid &= form.is_valid()
        return forms_valid and not self.non_form_errors()

    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms]

    def bulk_save(self):
        raise NotImplementedError("")  # TODO


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

