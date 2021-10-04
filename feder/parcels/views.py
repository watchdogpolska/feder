from atom.views import DeleteMessageMixin
from braces.views import (
    SelectRelatedMixin,
    UserFormKwargsMixin,
    FormValidMessageMixin,
    SetHeadlineMixin,
)
from cached_property import cached_property
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _

from feder.cases.models import Case
from feder.main.mixins import RaisePermissionRequiredMixin, BaseDetailFileRedirect
from feder.parcels.forms import IncomingParcelPostForm, OutgoingParcelPostForm
from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost


class ParcelPostDetailView(SelectRelatedMixin, DetailView):
    select_related = ["record__case__monitoring"]

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class CaseMixin:
    case = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["case"] = self.case
        return kwargs


class ParcelPostCreateView(
    RaisePermissionRequiredMixin,
    SetHeadlineMixin,
    CaseMixin,
    UserFormKwargsMixin,
    CreateView,
):
    permission_required = "monitorings.add_parcelpost"

    @cached_property
    def case(self):
        qs = Case.objects.select_related("monitoring").for_user(self.request.user)
        return get_object_or_404(qs, pk=self.kwargs["case_pk"])

    def get_object(self, *args, **kwargs):
        return self.case

    def get_permission_object(self):
        return self.case.monitoring

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.case
        return context

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)


class ParcelPostUpdateView(
    SetHeadlineMixin,
    RaisePermissionRequiredMixin,
    CaseMixin,
    UserFormKwargsMixin,
    FormValidMessageMixin,
    UpdateView,
):
    permission_required = "monitorings.change_parcelpost"

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            self._object = super().get_object(*args, **kwargs)
        return self._object

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)

    @property
    def case(self):
        return self.get_object().case

    def get_permission_object(self):
        return self.case.monitoring

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class ParcelPostDeleteView(
    RaisePermissionRequiredMixin, DeleteMessageMixin, DeleteView
):
    permission_required = "monitorings.delete_parcelpost"

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            self._object = super().get_object(*args, **kwargs)
        return self._object

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)

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


class AttachmentParcelPostXSendFileView(BaseDetailFileRedirect):
    file_field = "content"


class OutgoingAttachmentParcelPostXSendFileView(AttachmentParcelPostXSendFileView):
    model = OutgoingParcelPost


class IncomingAttachmentParcelPostXSendFileView(AttachmentParcelPostXSendFileView):
    model = IncomingParcelPost
