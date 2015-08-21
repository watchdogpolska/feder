from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin, PrefetchRelatedMixin)
from django.core.urlresolvers import reverse_lazy
from django_filters.views import FilterView
from guardian.mixins import PermissionRequiredMixin
from atom.views import DeleteMessageMixin, CreateMessageMixin, UpdateMessageMixin
from feder.monitorings.models import Monitoring
from .models import Case
from .forms import CaseForm
from .filters import CaseFilter


_("Case index")


class CaseListView(SelectRelatedMixin, FilterView):
    filterset_class = CaseFilter
    model = Case
    select_related = ['user', 'monitoring', 'institution']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(CaseListView, self).get_queryset(*args, **kwargs)
        return qs.with_letter_count()


class CaseDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Case
    select_related = ['user', 'monitoring', 'institution']
    prefetch_related = ['letter_set']

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        context['letter_list'] = (self.object.letter_set.for_milestone().all())
        return context


class CaseCreateView(LoginRequiredMixin, PermissionRequiredMixin, UserFormKwargsMixin,
        CreateMessageMixin, CreateView):
    model = Case
    form_class = CaseForm
    permission_required = 'monitorings.add_case'
    raise_exception = True

    def get_permission_object(self):
        self.monitoring = get_object_or_404(Monitoring, pk=self.kwargs['monitoring'])
        return self.monitoring

    def get_form_kwargs(self, *args, **kwargs):
        kw = super(CaseCreateView, self).get_form_kwargs(*args, **kwargs)
        kw['monitoring'] = self.monitoring
        return kw


class CaseUpdateView(LoginRequiredMixin, UserFormKwargsMixin, PermissionRequiredMixin,
        UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Case
    form_class = CaseForm
    permission_required = 'monitorings.change_case'
    raise_exception = True

    def get_permission_object(self):
        return super(CaseUpdateView, self).get_permission_object().monitoring


class CaseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteMessageMixin,
        DeleteView):
    model = Case
    success_url = reverse_lazy('cases:list')
    permission_required = 'monitorings.delete_case'
    raise_exception = True

    def get_permission_object(self):
        return super(CaseDeleteView, self).get_permission_object().monitoring
