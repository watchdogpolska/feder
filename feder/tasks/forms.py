# -*- coding: utf-8 -*-
from django import forms
from .models import Task
from atom.forms import SaveButtonMixin
from braces.forms import UserKwargModelFormMixin


class TaskForm(SaveButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Task
        fields = ['case', 'questionary', ]
