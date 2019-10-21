import unicodecsv as csv
from braces.views import FormValidMessageMixin, SetHeadlineMixin, UserFormKwargsMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, View
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
)

from feder.main.mixins import RaisePermissionRequiredMixin
from feder.tasks.forms import MultiTaskForm
from feder.tasks.models import Survey
from ..models import Questionary


def chain(*args):
    for obj in args:
        for row in obj:
            yield row


class TaskMultiCreateView(
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    FormValidMessageMixin,
    SingleObjectTemplateResponseMixin,
    SingleObjectMixin,
    SetHeadlineMixin,
    FormView,
):
    model = Questionary
    form_class = MultiTaskForm
    template_name_suffix = "_form"
    permission_required = "monitorings.add_task"
    headline = _("Create tasks")

    def get_permission_object(self):
        self.object = self.get_object()
        return super(TaskMultiCreateView, self).get_permission_object().monitoring

    def get_form_kwargs(self):
        kwargs = super(TaskMultiCreateView, self).get_form_kwargs()
        kwargs.update({"questionary": self.object})
        return kwargs

    def get_form_valid_message(self):
        return _("Tasks for {questionary} created!").format(questionary=self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.save()
        return super(TaskMultiCreateView, self).form_valid(form)


class SurveyCSVView(View):
    def get_filename(self):
        return 'attachment; filename="questionary-{pk}.csv"'.format(
            pk=self.kwargs["pk"]
        )

    def header(self, writer):
        col_unflatten = [
            x.modulator.get_label_column(x.definition)
            for x in self.questionary.question_set.all()
        ]
        content = list(chain(*col_unflatten))
        standard = ["Office", "Survey PK", "Credibility", "User"]
        writer.writerow(standard + content)

    def _get_row(self, survey):
        row_unflatten = [x.get_answer_columns() for x in survey.answer_set.all()]
        standard = [
            survey.task.case.institution,
            survey.pk,
            survey.credibility,
            survey.user,
        ]
        answer = list(chain(*row_unflatten))
        return standard + answer

    def body(self, writer):
        survey_list = (
            Survey.objects.filter(task__questionary=self.questionary)
            .select_related("task__case__institution", "user")
            .all()
        )
        for survey in survey_list:
            writer.writerow(self._get_row(survey))

    def get(self, request, pk, *args, **kwargs):
        self.questionary = get_object_or_404(Questionary, pk=pk)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = self.get_filename()
        writer = csv.writer(response)
        self.header(writer)
        self.body(writer)
        return response
