# Create your views here.
from django.shortcuts import get_object_or_404
from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from feder.cases.models import Case
from feder.main.mixins import AttrPermissionRequiredMixin, RaisePermissionRequiredMixin
from .filters import LetterFilter
from .forms import LetterForm
from .models import Letter

_("Letters index")


class LetterListView(UserKwargFilterSetMixin, SelectRelatedMixin, FilterView):
    filterset_class = LetterFilter
    model = Letter
    select_related = ['author_user', 'author_institution', 'case__institution']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(LetterListView, self).get_queryset(*args, **kwargs)
        return qs.attachment_count()


class LetterDetailView(SelectRelatedMixin, DetailView):
    model = Letter
    select_related = ['author_institution', 'author_user', 'case__monitoring']


class LetterCreateView(RaisePermissionRequiredMixin, UserFormKwargsMixin,
                       CreateMessageMixin, CreateView):
    model = Letter
    form_class = LetterForm
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.add_letter'
    raise_exception = True

    def get_case(self):
        self.case = get_object_or_404(Case.objects.select_related('monitoring'),
                                      pk=self.kwargs['case_pk'])
        return self.case

    def get_permission_object(self):
        return self.get_case().monitoring

    def get_form_kwargs(self):
        kw = super(LetterCreateView, self).get_form_kwargs()
        kw['case'] = self.case
        return kw


class LetterUpdateView(AttrPermissionRequiredMixin, UserFormKwargsMixin,
                       UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Letter
    form_class = LetterForm
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.change_letter'
    raise_exception = True


class LetterDeleteView(AttrPermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Letter
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.delete_letter'
    raise_exception = True

    def get_success_url(self):
        return self.object.case.get_absolute_url()
