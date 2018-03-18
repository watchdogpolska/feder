from django.test import TestCase
from django.urls import reverse

from feder.cases.factories import CaseFactory
from feder.main.mixins import PermissionStatusMixin
from feder.parcels.factories import IncomingParcelPostFactory, OutgoingParcelPostFactory


class ParcelPostMixin(object):
    def setUp(self):
        super(ParcelPostMixin, self).setUp()
        self.case = CaseFactory()
        self.permission_object = self.case.monitoring


class IncomingParcelPostMixin(ParcelPostMixin):
    def setUp(self):
        super(IncomingParcelPostMixin, self).setUp()
        self.object = IncomingParcelPostFactory(record__case=self.case)


class OutgoingParcelPostMixin(ParcelPostMixin):
    def setUp(self):
        super(OutgoingParcelPostMixin, self).setUp()
        self.object = OutgoingParcelPostFactory(record__case=self.case)


class IncomingParcelPostCreateViewTestCase(IncomingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_parcelpost', ]

    def get_url(self):
        return reverse('parcels:incoming-create', kwargs={'case_pk': self.case.pk})


class IncomingParcelPostDetailViewTestCase(IncomingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('parcels:incoming-details', kwargs={'pk': self.object.pk})


class IncomingParcelPostUpdateViewTestCase(IncomingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_parcelpost', ]

    def get_url(self):
        return reverse('parcels:incoming-update', kwargs={'pk': self.object.pk})


class IncomingParcelPostDeleteViewTestCase(IncomingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_parcelpost', ]

    def get_url(self):
        return reverse('parcels:incoming-delete', kwargs={'pk': self.object.pk})


class OutgoingParcelPostCreateViewTestCase(OutgoingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_parcelpost', ]

    def get_url(self):
        return reverse('parcels:outgoing-create', kwargs={'case_pk': self.case.pk})


class OutgoingParcelPostDetailViewTestCase(OutgoingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('parcels:outgoing-details', kwargs={'pk': self.object.pk})


class OutgoingParcelPostUpdateViewTestCase(OutgoingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_parcelpost', ]

    def get_url(self):
        return reverse('parcels:outgoing-update', kwargs={'pk': self.object.pk})


class OutgoingParcelPostDeleteViewTestCase(OutgoingParcelPostMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_parcelpost', ]

    def get_url(self):
        return reverse('parcels:outgoing-delete', kwargs={'pk': self.object.pk})
