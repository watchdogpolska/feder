import datetime

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from feder.cases.models import Case
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

    def test_create_new_parcel(self):
        self.login_permitted_user()
        simple_file = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4"
        )
        resp = self.client.post(
            self.get_url(),
            data={
                "title": "xxx",
                "content": "yyy",
                "content": simple_file,
                "sender": self.object.sender.pk,
                "receive_date": self.object.receive_date,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(self.case.record_set.count(), 2)


class IncomingParcelPostDetailViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("parcels:incoming-details", kwargs={"pk": self.object.pk})

    def test_hide_letter_from_quarantined_case(self):
        Case.objects.filter(pk=self.case.pk).update(is_quarantined=True)
        response = self.client.get(self.get_url())
        self.assertNotContains(response, self.object, status_code=404)

    def test_show_quarantined_letter_for_authorized(self):
        Case.objects.filter(pk=self.case.pk).update(is_quarantined=True)
        self.grant_permission("monitorings.view_quarantined_case")
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertContains(response, self.object)


class IncomingAttachmentParcelPostXSendFileViewTestCase(
    IncomingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 302
    status_no_permission = 302
    status_has_permission = 302

    def get_url(self):
        return reverse("parcels:incoming-download", kwargs={"pk": self.object.pk})


class OutgoingAttachmentParcelPostXSendFileViewTestCase(
    OutgoingParcelPostMixin, PermissionStatusMixin, TestCase
):
    permission = []
    status_anonymous = 302
    status_no_permission = 302
    status_has_permission = 302

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
        resp = self.client.post(
            self.get_url(),
            data={
                "title": "xxx",
                "content": "yyy",
                "sender": self.object.sender.pk,
                "receive_date": self.object.receive_date,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.object.refresh_from_db()
        self.assertEqual(self.object.title, "xxx")
        self.assertEqual(self.object.record.id, previous_record)

    def test_update_time_of_parcel(self):
        self.login_permitted_user()
        new_date = self.object.receive_date + datetime.timedelta(days=25)
        resp = self.client.post(
            self.get_url(),
            data={
                "title": "xxx",
                "content": "yyy",
                "sender": self.object.sender.pk,
                "receive_date": new_date,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.object.refresh_from_db()
        self.assertEqual(self.object.receive_date, new_date)
        self.assertTrue(self.case.record_set.count(), 1)


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

    def test_create_new_parcel(self):
        self.login_permitted_user()
        simple_file = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4"
        )
        resp = self.client.post(
            self.get_url(),
            data={
                "title": "xxx",
                "content": "yyy",
                "content": simple_file,
                "recipient": self.object.recipient.pk,
                "post_date": self.object.post_date,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(self.case.record_set.count(), 2)


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
