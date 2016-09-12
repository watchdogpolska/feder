from atom.views import (CreateMessageMixin, DeleteMessageMixin,
                        UpdateMessageMixin)
from braces.views import (FormValidMessageMixin, LoginRequiredMixin,
                          PermissionRequiredMixin, PrefetchRelatedMixin,
                          SelectRelatedMixin, UserFormKwargsMixin)
from dal import autocomplete
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from feder.cases.models import Case
from feder.main.mixins import ExtraListMixin

from .filters import InstitutionFilter
from .forms import InstitutionForm
from .models import Institution, Tag

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
    redirect_unauthenticated_users = True


class InstitutionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UserFormKwargsMixin,
                            UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    permission_required = "institutions.change_institution"
    raise_exception = True
    redirect_unauthenticated_users = True


class InstitutionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteMessageMixin,
                            UpdateMessageMixin, DeleteView):
    model = Institution
    success_url = reverse_lazy('institutions:list')
    permission_required = "institutions.delete_institution"
    raise_exception = True
    redirect_unauthenticated_users = True


class InstitutionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Institution.objects
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.all()


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.annotate(institution_count=Count('institution'))
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by('-institution_count').all()

    def get_result_label(self, result):
        return "%s (%d)" % (six.text_type(result), result.institution_count)
