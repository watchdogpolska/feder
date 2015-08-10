# -*- coding: utf-8 -*-
from django import forms
from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin
from feder.cases.models import Case
from .models import Task


class TaskForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ['case', 'questionary', ]


class MultiTaskForm(SaveButtonMixin, UserKwargModelFormMixin, forms.Form):
    cases = forms.ModelMultipleChoiceField(queryset=Case.objects.none())

    def __init__(self, questionary, *args, **kwargs):
        self.questionary = questionary
        super(MultiTaskForm, self).__init__(*args, **kwargs)
        self.fields['cases'].queryset = questionary.monitoring.case_set.all()

    def save(self, *args, **kwargs):
        objs = [Task(questionary=self.questionary, case=case)
            for case in self.cleaned_data['cases']]
        return Task.objects.bulk_create(objs)
