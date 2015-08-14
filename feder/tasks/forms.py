# -*- coding: utf-8 -*-
from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from feder.cases.models import Case
from feder.questionaries.modulator import modulators
from .models import Task, Survey, Answer


class TaskForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ['case', 'questionary', ]


class AnswerForm(forms.Form):
    def __init__(self, question, survey=None, *args, **kwargs):
        self.question = question
        self.survey = survey
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.modulator = modulators[question.genre](question.blob)
        self.modulator.answer(self.fields)

    def save(self, commit=True):
        obj = Answer(survey=self.survey, question=self.question)
        obj.blob = self.modulator.read(self.cleaned_data)
        if commit:
            obj.save()
        return obj


class AnswerFormSet(object):  # How use django formsets?
    def __init__(self, questionary, survey=None, *args, **kwargs):
        self.questionary = questionary
        self.survey = survey
        self.args = args
        self.kwargs = kwargs
        self.is_bound = (self.kwargs.get('data', None) is not None
            or self.kwargs.get('files', None) is not None)

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
        forms = [AnswerForm(question=question, survey=self.survey, prefix=str(question.pk),
                *self.args, **self.kwargs)
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
        return forms_valid  # and not self.non_form_errors()

    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms]

    def bulk_save(self):
        raise NotImplementedError("")  # TODO


class MultiTaskForm(SaveButtonMixin, UserKwargModelFormMixin, forms.Form):
    cases = forms.ModelMultipleChoiceField(queryset=Case.objects.none(), label=_("Cases"))
    name = forms.CharField(max_length=50, label=_("Name"))

    def __init__(self, questionary, *args, **kwargs):
        self.questionary = questionary
        super(MultiTaskForm, self).__init__(*args, **kwargs)
        self.fields['cases'].queryset = questionary.monitoring.case_set.all()

    def get_name(self, no):
        return "{name} #{no}".format(name=self.cleaned_data['name'], no=no)

    def save(self, *args, **kwargs):
        objs = [Task(questionary=self.questionary, name=self.get_name(no),
            case=case) for no, case in enumerate(self.cleaned_data['cases'], start=1)]
        return Task.objects.bulk_create(objs)


class SurveyForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task')
        super(SurveyForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.task = self.task
        self.instance.user = self.user
        return super(SurveyForm, self).save(*args, **kwargs)

    class Meta:
        model = Survey
        fields = []
