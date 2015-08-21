from django.views.generic import DetailView
from django_filters.views import FilterView
from braces.views import SelectRelatedMixin, PrefetchRelatedMixin
from feder.cases.models import Case
from feder.main.mixins import ExtraListMixin
from .models import Institution
from .filters import InstitutionFilter
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from braces.views import (LoginRequiredMixin, PermissionRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin)
from django.core.urlresolvers import reverse_lazy
from atom.views import DeleteMessageMixin, CreateMessageMixin, UpdateMessageMixin
from .forms import InstitutionForm

_('Institutions index')


class InstitutionListView(SelectRelatedMixin, FilterView):
    filterset_class = InstitutionFilter
    model = Institution
    select_related = ['jst', 'jst__category']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(InstitutionListView, self).get_queryset(*args, **kwargs)
        return qs.with_case_count()


class InstitutionDetailView(SelectRelatedMixin, ExtraListMixin, PrefetchRelatedMixin, DetailView):
    model = Institution
    prefetch_related = ['tags']
    select_related = []
    extra_list_context = 'case_list'

    @staticmethod
    def get_object_list(obj):
        return (Case.objects.filter(institution=obj).
            select_related('monitoring').
            prefetch_related('task_set').
            order_by('monitoring').all())


class InstitutionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateMessageMixin,
        UserFormKwargsMixin, CreateView):
    model = Institution
    form_class = InstitutionForm
    permission_required = "institutions.add_institution"
    raise_exception = True


class InstitutionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UserFormKwargsMixin,
        UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    permission_required = "institutions.change_institution"
    raise_exception = True


class InstitutionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteMessageMixin,
        UpdateMessageMixin, DeleteView):
    model = Institution
    success_url = reverse_lazy('institutions:list')
    permission_required = "institutions.delete_institution"
    raise_exception = True
