from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from cached_property import cached_property
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from feder.main.mixins import AttrPermissionRequiredMixin, RaisePermissionRequiredMixin
from feder.monitorings.models import Monitoring
from feder.tasks.forms import AnswerFormSet
from ..filters import QuestionaryFilter
from ..forms import QuestionaryForm
from ..models import Questionary


class QuestionaryListView(UserKwargFilterSetMixin, SelectRelatedMixin, FilterView):
    filterset_class = QuestionaryFilter
    model = Questionary
    select_related = ["monitoring"]
    paginate_by = 25

    def get_filterset_kwargs(self, *args, **kwargs):
        kwargs = super(QuestionaryListView, self).get_filterset_kwargs(*args, **kwargs)
        kwargs["user"] = self.request.user
        return kwargs


class QuestionaryDetailView(PrefetchRelatedMixin, DetailView):
    model = Questionary
    prefetch_related = ["question_set"]

    def get_context_data(self, **kwargs):
        context = super(QuestionaryDetailView, self).get_context_data(**kwargs)
        context["answer_forms"] = AnswerFormSet(questionary=self.object)
        return context


class QuestionaryCreateView(
    RaisePermissionRequiredMixin, UserFormKwargsMixin, CreateMessageMixin, CreateView
):
    model = Questionary
    form_class = QuestionaryForm
    permission_required = "monitorings.add_questionary"

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, pk=self.kwargs["monitoring"])

    def get_permission_object(self):
        return self.monitoring

    def get_form_kwargs(self):
        kw = super(QuestionaryCreateView, self).get_form_kwargs()
        kw["monitoring"] = self.monitoring
        return kw


class QuestionaryUpdateView(
    AttrPermissionRequiredMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    UpdateView,
):
    model = Questionary
    form_class = QuestionaryForm
    permission_required = "monitorings.change_questionary"
    permission_attribute = "monitoring"


class QuestionaryDeleteView(
    AttrPermissionRequiredMixin, SelectRelatedMixin, DeleteMessageMixin, DeleteView
):
    model = Questionary
    permission_required = "monitorings.delete_questionary"
    permission_attribute = "monitoring"
    select_related = ["monitoring"]

    def get_success_url(self):
        return self.object.monitoring.get_absolute_url()
