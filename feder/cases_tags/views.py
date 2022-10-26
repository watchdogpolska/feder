from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)

from cached_property import cached_property
from dal import autocomplete
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)

from feder.main.mixins import RaisePermissionRequiredMixin
from feder.monitorings.models import Monitoring
from django_filters.views import FilterView

from django.db.models import Count
from .models import Tag
from .forms import TagForm
from .filters import TagFilter

_("Tag index")


class MonitoringPermissionMixin(RaisePermissionRequiredMixin):
    def get_permission_object(self):
        return self.monitoring

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, pk=self.kwargs["monitoring"])

    def get_queryset(self):
        return super().get_queryset().for_monitoring(self.monitoring)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring"] = self.monitoring
        return context


class TagListView(
    SelectRelatedMixin,
    MonitoringPermissionMixin,
    FilterView,
):
    filterset_class = TagFilter
    model = Tag
    select_related = ["monitoring"]
    paginate_by = 25
    permission_required = "monitorings.view_tag"


class TagDetailView(MonitoringPermissionMixin, SelectRelatedMixin, DetailView):
    model = Tag
    select_related = ["monitoring"]
    permission_required = "monitorings.view_tag"


class TagCreateView(
    MonitoringPermissionMixin, UserFormKwargsMixin, CreateMessageMixin, CreateView
):
    model = Tag
    form_class = TagForm
    permission_required = "monitorings.change_tag"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["monitoring"] = self.monitoring
        return kw


class TagUpdateView(
    MonitoringPermissionMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    UpdateView,
):
    model = Tag
    form_class = TagForm
    permission_required = "monitorings.change_tag"


class TagDeleteView(MonitoringPermissionMixin, DeleteMessageMixin, DeleteView):
    model = Tag
    permission_required = "monitorings.delete_tag"

    def get_success_url(self) -> str:
        return reverse(
            "cases_tags:list", kwargs={"monitoring": super().get_permission_object().pk}
        )

    def get_success_message(self):
        return _("{object} deleted!").format(object=self.object)


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_monitoring(self, pk):
        return get_object_or_404(Monitoring.objects.for_user(self.request.user), pk=pk)

    def get_queryset(self):
        monitoring = self.get_monitoring(pk=self.kwargs["monitoring"])

        qs = Tag.objects.for_monitoring(monitoring).annotate(count=Count("monitoring"))
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

    def get_result_label(self, result):
        return "%s (%d)" % (str(result), result.count)
