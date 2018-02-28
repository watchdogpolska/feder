# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from atom.views import DeleteMessageMixin
from braces.views import SelectRelatedMixin, UserFormKwargsMixin, FormValidMessageMixin, SetHeadlineMixin
from cached_property import cached_property
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from guardian.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _

from feder.cases.models import Case
from feder.main.mixins import RaisePermissionRequiredMixin
from feder.parcels.forms import IncomingParcelPostForm, OutgoingParcelPostForm
from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost


class ParcelPostDetailView(SelectRelatedMixin, DetailView):
    select_related = ['record__case__monitoring', ]


class ParcelPostCreateView(RaisePermissionRequiredMixin, UserFormKwargsMixin, CreateView):
    permission_required = 'monitorings.add_parcelpost'

    @cached_property
    def case(self):
        return get_object_or_404(Case, pk=self.kwargs['case_pk'])

    def get_object(self, *args, **kwargs):
        return self.case

    def get_form_kwargs(self):
        kwargs = super(ParcelPostCreateView, self).get_form_kwargs()
        kwargs['case'] = self.case
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ParcelPostCreateView, self).get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)


class ParcelPostUpdateView(RaisePermissionRequiredMixin, UserFormKwargsMixin, FormValidMessageMixin, UpdateView):
    permission_required = 'monitorings.change_parcelpost'

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class ParcelPostDeleteView(RaisePermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    permission_required = 'monitorings.delete_parcelpost'

    def get_success_url(self):
        return self.object.record.case.monitoring

    def get_success_message(self):
        return _("{0} deleted!").format(self.object)


class IncomingParcelPostDetailView(ParcelPostDetailView):
    model = IncomingParcelPost


class IncomingParcelPostCreateView(SetHeadlineMixin, ParcelPostCreateView):
    model = IncomingParcelPost
    form_class = IncomingParcelPostForm
    headline = _("Add incoming parcel post")


class IncomingParcelPostUpdateView(ParcelPostUpdateView):
    model = IncomingParcelPost
    form_class = IncomingParcelPostForm


class IncomingParcelPostDeleteView(ParcelPostDeleteView):
    model = IncomingParcelPost
    form_class = IncomingParcelPostForm


class OutgoingParcelPostDetailView(ParcelPostDetailView):
    model = OutgoingParcelPost
    form_class = OutgoingParcelPostForm


class OutgoingParcelPostCreateView(SetHeadlineMixin, ParcelPostCreateView):
    model = OutgoingParcelPost
    form_class = OutgoingParcelPostForm
    headline = _("Add outgoing parcel post")


class OutgoingParcelPostUpdateView(SetHeadlineMixin, ParcelPostUpdateView):
    model = OutgoingParcelPost
    form_class = OutgoingParcelPostForm


class OutgoingParcelPostDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = IncomingParcelPost
