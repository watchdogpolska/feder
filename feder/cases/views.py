from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from cached_property import cached_property
from dal import autocomplete
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from feder.main.mixins import (
    DisableOrderingListViewMixin,
    PerformantPagintorMixin,
    RaisePermissionRequiredMixin,
)
from feder.main.utils import DeleteViewLogEntryMixin, FormValidLogEntryMixin
from feder.monitorings.models import Monitoring

from .filters import CaseFilter
from .forms import CaseForm
from .models import Case

_("Case index")


class CaseListView(
    SelectRelatedMixin,
    DisableOrderingListViewMixin,
    PerformantPagintorMixin,
    FilterView,
):
    filterset_class = CaseFilter
    model = Case
    select_related = ["user", "monitoring", "institution"]
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class CaseDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Case
    select_related = ["user", "monitoring", "institution"]
    prefetch_related = ["record_set"]

    def get_queryset(self):
        return super().get_queryset().with_milestone().for_user(self.request.user)


class CaseCreateView(
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    CreateMessageMixin,
    FormValidLogEntryMixin,
    CreateView,
):
    model = Case
    form_class = CaseForm
    permission_required = "monitorings.add_case"

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, pk=self.kwargs["monitoring"])

    def get_permission_object(self):
        return self.monitoring

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["monitoring"] = self.monitoring
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring"] = self.monitoring
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_email()
        return response


class CaseUpdateView(
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    FormValidLogEntryMixin,
    UpdateView,
):
    model = Case
    form_class = CaseForm
    permission_required = "monitorings.change_case"

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)

    def get_permission_object(self):
        return super().get_permission_object().monitoring

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_email()
        return response


class CaseDeleteView(
    RaisePermissionRequiredMixin,
    DeleteMessageMixin,
    DeleteViewLogEntryMixin,
    DeleteView,
):
    model = Case
    success_url = reverse_lazy("cases:list")
    permission_required = "monitorings.delete_case"

    def get_permission_object(self):
        return super().get_permission_object().monitoring

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class CaseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Case.objects.all().order_by().for_user(self.request.user)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class CaseFindAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Case.objects.all().order_by().for_user(self.request.user)

        if self.q:
            qs = qs.filter(
                Q(pk__startswith=self.q)
                | Q(institution__name__icontains=self.q)
                | Q(name__icontains=self.q)
            )

        return qs

    def get_result_label(self, result):
        return "#{} - {} - {}".format(
            str(result.pk), str(result.institution), str(result)
        )
