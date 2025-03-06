from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from dal import autocomplete
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from feder.cases.models import Case
from feder.main.mixins import ExtraListMixin
from feder.main.paginator import DefaultPagination
from feder.main.utils import DeleteViewLogEntryMixin, FormValidLogEntryMixin

from .filters import InstitutionFilter
from .forms import InstitutionForm
from .models import Institution, Tag

_("Institutions index")


class InstitutionListView(SelectRelatedMixin, FilterView):
    filterset_class = InstitutionFilter
    model = Institution
    select_related = ["jst", "jst__category"]
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.with_case_count().order_by("name")

    def get_context_data(self, *args, **kwargs):
        params = [["format", "csv"], ["page_size", DefaultPagination.max_page_size]]
        context = super().get_context_data(*args, **kwargs)

        for name in ("name", "tags", "regon", "voivodeship", "county", "community"):
            api_name = "jst" if name in ("voivodeship", "county", "community") else name
            val_list = self.request.GET.getlist(name)
            if val_list:
                for val in val_list:
                    if val:
                        params.append([api_name, val])

        context["csv_url"] = "{}?{}".format(
            reverse_lazy("institution-list"), urlencode(params)
        )
        return context


class InstitutionDetailView(ExtraListMixin, PrefetchRelatedMixin, DetailView):
    model = Institution
    prefetch_related = ["tags"]
    extra_list_context = "case_list"

    def get_object_list(self, obj):
        return (
            Case.objects.filter(institution=obj)
            .select_related("monitoring")
            .order_by("monitoring__name")
            .all()
            .for_user(self.request.user)
        )


class InstitutionCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateMessageMixin,
    UserFormKwargsMixin,
    FormValidLogEntryMixin,
    CreateView,
):
    model = Institution
    form_class = InstitutionForm
    permission_required = "institutions.add_institution"
    raise_exception = True
    redirect_unauthenticated_users = True


class InstitutionUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    FormValidLogEntryMixin,
    UpdateView,
):
    model = Institution
    form_class = InstitutionForm
    permission_required = "institutions.change_institution"
    raise_exception = True
    redirect_unauthenticated_users = True


class InstitutionDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteMessageMixin,
    UpdateMessageMixin,
    DeleteViewLogEntryMixin,
    DeleteView,
):
    model = Institution
    success_url = reverse_lazy("institutions:list")
    permission_required = "institutions.delete_institution"
    raise_exception = True
    redirect_unauthenticated_users = True


class InstitutionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Institution.objects
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.all().order_by("name")

    def get_result_label(self, result):
        return f"{result.name_with_jst}"


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.annotate(institution_count=Count("institution"))
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by("name")

    def get_result_label(self, result):
        return "%s (%d)" % (str(result), result.institution_count)
