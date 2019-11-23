from django.test import TestCase
from django.urls import reverse

from feder.cases.factories import CaseFactory
from feder.main.tests import PermissionStatusMixin
from feder.parcels.factories import IncomingParcelPostFactory, OutgoingParcelPostFactory


class ParcelPostMixin:
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()
        self.permission_object = self.case.monitoring


class IncomingParcelPostMixin(ParcelPostMixin):
    def setUp(self):
        super().setUp()
        self.object = IncomingParcelPostFactory(record__case=self.case)


class OutgoingParcelPostMixin(ParcelPostMixin):
    def setUp(self):
        super().setUp()
        self.object = OutgoingParcelPostFactory(record__case=self.case)


class IncomingParcelPostCreateViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.add_parcelpost"]

    def get_url(self):
        return reverse("parcels:incoming-create", kwargs={"case_pk": self.case.pk})


class IncomingParcelPostDetailViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("parcels:incoming-details", kwargs={"pk": self.object.pk})


class IncomingAttachmentParcelPostXSendFileViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("parcels:incoming-download", kwargs={"pk": self.object.pk})


class OutgoingAttachmentParcelPostXSendFileViewTestCase(
    OutgoingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("parcels:outgoing-download", kwargs={"pk": self.object.pk})


class IncomingParcelPostUpdateViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.change_parcelpost"]

    def get_url(self):
        return reverse("parcels:incoming-update", kwargs={"pk": self.object.pk})

    def test_avoid_duplicate_record_on_update(self):
        self.login_permitted_user()
        previous_record = self.object.record.id

        self.client.post(
            self.get_url(),
            data={
                "title": "xxx",
                "content": "yyy",
                "sender": self.object.sender.pk,
                "receive_date": self.object.receive_date,
            },
        )
        self.object.refresh_from_db()
        self.assertEqual(self.object.title, "xxx")
        self.assertEqual(self.object.record.id, previous_record)


class IncomingParcelPostDeleteViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.delete_parcelpost"]

    def get_url(self):
        return reverse("parcels:incoming-delete", kwargs={"pk": self.object.pk})


class OutgoingParcelPostCreateViewTestCase(
    OutgoingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.add_parcelpost"]

    def get_url(self):
        return reverse("parcels:outgoing-create", kwargs={"case_pk": self.case.pk})


class OutgoingParcelPostDetailViewTestCase(
    OutgoingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("parcels:outgoing-details", kwargs={"pk": self.object.pk})


class OutgoingParcelPostUpdateViewTestCase(
    OutgoingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.change_parcelpost"]

    def get_url(self):
        return reverse("parcels:outgoing-update", kwargs={"pk": self.object.pk})


class OutgoingParcelPostDeleteViewTestCase(
    OutgoingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.delete_parcelpost"]

    def get_url(self):
        return reverse("parcels:outgoing-delete", kwargs={"pk": self.object.pk})
