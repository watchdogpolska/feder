from atom.views import (
    ActionMessageMixin,
    ActionView,
    CreateMessageMixin,
    UpdateMessageMixin,
    DeleteMessageMixin,
)
from braces.views import FormValidMessageMixin, SelectRelatedMixin
from cached_property import cached_property
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView

from feder.main.mixins import AttrPermissionRequiredMixin
from ..forms import QuestionDefinitionForm, QuestionForm
from ..models import Question, Questionary


class QuestionCreateView(
    AttrPermissionRequiredMixin, CreateMessageMixin, FormValidMessageMixin, CreateView
):
    model = Question
    template_name = "questionaries/question_form.html"
    form_class = QuestionForm
    permission_required = "monitorings.change_questionary"

    @cached_property
    def questionary(self):
        return get_object_or_404(Questionary, pk=self.kwargs["pk"])

    def get_permission_object(self):
        return self.questionary.monitoring

    def get_form_kwargs(self):
        kw = super(QuestionCreateView, self).get_form_kwargs()
        kw["questionary"] = self.questionary
        return kw

    def get_success_url(self):
        if not self.object.definition:
            return self.object.get_absolute_url()
        return self.questionary.get_absolute_url()


class QuestionUpdateView(
    AttrPermissionRequiredMixin, UpdateMessageMixin, FormValidMessageMixin, UpdateView
):
    model = Question
    template_name = "questionaries/question_form.html"
    form_class = QuestionDefinitionForm
    permission_required = "monitorings.change_questionary"
    permission_attribute = "questionary__monitoring"

    def get_success_url(self):
        return self.object.questionary.get_absolute_url()


class QuestionMoveView(
    AttrPermissionRequiredMixin, ActionMessageMixin, SelectRelatedMixin, ActionView
):
    model = Question
    template_name_suffix = "_move"
    direction = None
    select_related = ["questionary__monitoring"]
    permission_required = "monitorings.change_questionary"
    permission_attribute = "questionary__monitoring"
    change = {"up": -1, "down": +1}

    def action(self, *args, **kwargs):
        self.object.position = F("position") + self.change[self.direction]
        self.object.save()

    def get_success_message(self):
        return _("Question {object} moved!").format(object=self.object)

    def get_success_url(self):
        return self.object.questionary.get_absolute_url()


class QuestionDeleteView(AttrPermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Question
    permission_required = "monitorings.change_questionary"
    permission_attribute = "questionary__monitoring"

    def get_success_url(self):
        return self.object.questionary.get_absolute_url()
