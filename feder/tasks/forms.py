# -*- coding: utf-8 -*-
from atom.ext.crispy_forms.forms import HelperMixin, SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from feder.cases.models import Case
from .models import Answer, Survey, Task


class TaskForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if self.case:
            self.instance.case = self.case

    class Meta:
        model = Task
        fields = ['name', 'questionary', 'survey_required']


class AnswerForm(HelperMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.modulator = self.question.modulator
        self.survey = kwargs.pop('survey', None)
        self.instance = kwargs.pop('instance', Answer())
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.construct_form()
        self.helper.form_tag = False

    def construct_form(self):
        fields = self.modulator.list_create_answer_fields(self.question.definition)
        for name, field in fields:
            self.fields[name] = field
            if name in self.initial:
                self.fields[name].initial = self.initial[name]

    def save(self, commit=True):
        self.instance.survey = self.survey
        self.instance.question = self.question
        self.instance.content = self.modulator.get_content(self.question.definition,
                                                           self.cleaned_data)
        if commit:
            self.instance.save()
        return self.instance


class AnswerFormSet(object):
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
        return iter(self.forms)

    def __getitem__(self, index):
        return self.forms[index]

    def __len__(self):
        return len(self.forms)

    def get_form_kwargs(self, question):
        return dict(question=question,
                    survey=self.survey,
                    prefix=str(question.pk),
                    initial=self.initial.get(question.pk, {}),
                    instance=self.instances.get(question.pk, Answer()),
                    **self.kwargs)

    @cached_property
    def instances(self):
        """
        Identifiy instances each form at first property access.
        """
        if not self.survey:
            return {}
        items = []
        for x in self.survey.answer_set.all():
            items.append((x.question.pk, x))
        return dict(items)

    @cached_property
    def initial(self):
        """
        Generate initial values for each form at first property access.
        """
        if not self.survey:
            return {}
        items = []
        for x in self.survey.answer_set.all():
            initial = x.question.modulator.get_initial(x.question.definition, x.content)
            items.append((x.question.pk, initial))
        return dict(items)

    @cached_property
    def forms(self):
        """
        Instantiate forms at first property access.
        """
        return [AnswerForm(*self.args, **self.get_form_kwargs(question))
                for question in self.questionary.question_set.all()]

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


class MultiTaskForm(SingleButtonMixin, UserKwargModelFormMixin, forms.Form):
    cases = forms.ModelMultipleChoiceField(queryset=Case.objects.none(), label=_("Cases"))
    suffix = forms.CharField(max_length=50, label=_("Suffix"),
                             help_text=_('Suffix for name in the form "[suffix] #[no]".'))

    def __init__(self, questionary, *args, **kwargs):
        self.questionary = questionary
        super(MultiTaskForm, self).__init__(*args, **kwargs)
        self.fields['cases'].queryset = questionary.monitoring.case_set.all()
        self.fields['cases'].help_text = _("They are available only cases " +
                                           "relevant to the monitoring.")

    def get_name(self, no):
        return u"{suffix} #{no}".format(suffix=self.cleaned_data['suffix'], no=no)

    def save(self, *args, **kwargs):
        objs = [Task(questionary=self.questionary, name=self.get_name(no),
                     case=case) for no, case in enumerate(self.cleaned_data['cases'], start=1)]
        return Task.objects.bulk_create(objs)


class SurveyForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task')
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.instance.task = self.task
        self.instance.user = self.user

    class Meta:
        model = Survey
        fields = []
