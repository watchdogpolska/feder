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
from feder.letters.views import MixinGzipXSendFile
from feder.main.mixins import RaisePermissionRequiredMixin, BaseXSendFileView
from feder.parcels.forms import IncomingParcelPostForm, OutgoingParcelPostForm
from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost


class ParcelPostDetailView(SelectRelatedMixin, DetailView):
    select_related = ['record__case__monitoring', ]


class CaseMixin(object):
    case = None

    def get_form_kwargs(self):
        kwargs = super(CaseMixin, self).get_form_kwargs()
        kwargs['case'] = self.case
        return kwargs


class ParcelPostCreateView(RaisePermissionRequiredMixin, SetHeadlineMixin, CaseMixin, UserFormKwargsMixin, CreateView):
    permission_required = 'monitorings.add_parcelpost'

    @cached_property
    def case(self):
        return get_object_or_404(Case.objects.select_related('monitoring'), pk=self.kwargs['case_pk'])

    def get_object(self, *args, **kwargs):
        return self.case

    def get_permission_object(self):
        return self.case.monitoring

    def get_context_data(self, **kwargs):
        context = super(ParcelPostCreateView, self).get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)


class ParcelPostUpdateView(SetHeadlineMixin, RaisePermissionRequiredMixin, CaseMixin, UserFormKwargsMixin,
                           FormValidMessageMixin, UpdateView):
    permission_required = 'monitorings.change_parcelpost'

    def get_object(self, *args, **kwargs):
        if not hasattr(self, '_object'):
            self._object = super(ParcelPostUpdateView, self).get_object(*args, **kwargs)
        return self._object

    @property
    def case(self):
        return self.get_object().case

    def get_permission_object(self):
        return self.case.monitoring

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class ParcelPostDeleteView(RaisePermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    permission_required = 'monitorings.delete_parcelpost'

    def get_object(self, *args, **kwargs):
        if not hasattr(self, '_object'):
            self._object = super(ParcelPostDeleteView, self).get_object(*args, **kwargs)
        return self._object

    def get_permission_object(self):
        return self.get_object().case.monitoring

    def get_success_url(self):
        return self.object.case.monitoring

    def get_success_message(self):
        return _("{0} deleted!").format(self.object)


class IncomingParcelPostDetailView(ParcelPostDetailView):
    model = IncomingParcelPost


class IncomingParcelPostCreateView(ParcelPostCreateView):
    model = IncomingParcelPost
    form_class = IncomingParcelPostForm
    headline = _("Add incoming parcel post")


class IncomingParcelPostUpdateView(ParcelPostUpdateView):
    model = IncomingParcelPost
    form_class = IncomingParcelPostForm
    headline = _("Update incoming parcel post")


class IncomingParcelPostDeleteView(ParcelPostDeleteView):
    model = IncomingParcelPost


class OutgoingParcelPostDetailView(ParcelPostDetailView):
    model = OutgoingParcelPost
    form_class = OutgoingParcelPostForm


class OutgoingParcelPostCreateView(ParcelPostCreateView):
    model = OutgoingParcelPost
    form_class = OutgoingParcelPostForm
    headline = _("Add outgoing parcel post")


class OutgoingParcelPostUpdateView(ParcelPostUpdateView):
    model = OutgoingParcelPost
    form_class = OutgoingParcelPostForm
    headline = _("Update outgoing parcel post")


class OutgoingParcelPostDeleteView(ParcelPostDeleteView):
    model = OutgoingParcelPost


class AttachmentParcelPostXSendFileView(BaseXSendFileView):
    file_field = 'content'
    send_as_attachment = True

    def get_queryset(self):
        return super(AttachmentParcelPostXSendFileView, self).get_queryset().for_user(self.request.user)


class OutgoingAttachmentParcelPostXSendFileView(AttachmentParcelPostXSendFileView):
    model = OutgoingParcelPost


class IncomingAttachmentParcelPostXSendFileView(AttachmentParcelPostXSendFileView):
    model = IncomingParcelPost
