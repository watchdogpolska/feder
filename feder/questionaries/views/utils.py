import csv
import itertools

from braces.views import (FormValidMessageMixin, SetHeadlineMixin,
                          UserFormKwargsMixin)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.detail import (SingleObjectMixin,
                                         SingleObjectTemplateResponseMixin)

from feder.main.mixins import RaisePermissionRequiredMixin
from feder.tasks.forms import MultiTaskForm
from feder.tasks.models import Survey

from ..models import Questionary


class TaskMultiCreateView(RaisePermissionRequiredMixin,
                          UserFormKwargsMixin,
                          FormValidMessageMixin,
                          SingleObjectTemplateResponseMixin,
                          SingleObjectMixin,
                          SetHeadlineMixin,
                          FormView):
    model = Questionary
    form_class = MultiTaskForm
    template_name_suffix = '_form'
    permission_required = 'monitorings.add_tasks'
    headline = _("Create tasks")

    def get_permission_object(self):
        self.object = self.get_object()
        return super(TaskMultiCreateView, self).get_permission_object().monitoring

    def get_form_kwargs(self):
        kwargs = super(TaskMultiCreateView, self).get_form_kwargs()
        kwargs.update({'questionary': self.object})
        return kwargs

    def get_form_valid_message(self):
        return _("Tasks for {questionary} created!").format(questionary=self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(TaskMultiCreateView, self).form_valid(form, *args, **kwargs)


def save_survey_as_csv(request, pk):
    questionary = get_object_or_404(Questionary, pk=pk)
    survey_list = (Survey.objects.filter(task__questionary=questionary).
                   select_related('task__case__institution', 'user').all())

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questionary-{pk}.csv"'.format(pk=pk)

    col_unflatten = [x.label(sheet=True) for x in questionary.question_set.all()]

    writer = csv.writer(response)
    writer.writerow(["Office", "Survey PK", "Credibility", 'User'] +
                    list(itertools.chain.from_iterable(col_unflatten)))
    for survey in survey_list:
        row_unflatten = [x.render(sheet=True) for x in survey.answer_set.all()]
        writer.writerow([survey.task.case.institution, survey.pk, survey.credibility, survey.user] +
                        list(itertools.chain.from_iterable(row_unflatten)))
    return response
