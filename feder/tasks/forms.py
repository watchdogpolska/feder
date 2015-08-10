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


class MultiTaskForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    cases = forms.ModelMultipleChoiceField(queryset=Case.objects.none())

    class Meta:
        model = Task
        fields = []

    def __init__(self, questionary, *args, **kwargs):
        self.questionary = questionary
        super(MultiTaskForm, self).__init__(*args, **kwargs)
        self.fields['cases'].queryset = questionary.monitoring.case_set.all()

    def save(self, commit=False, *args, **kwargs):
        objs = []
        for case in self.cleaned_data['cases']:
            obj = super(MultiTaskForm, self).save(commit=False, *args, **kwargs)
            obj.case = self.case
            obj.questionary = self.questionary
            obj.save()
            objs.append(obj)
        return objs
