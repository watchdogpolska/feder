from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from feder.cases.factories import CaseFactory
from feder.main.tests import PermissionStatusMixin
from feder.users.factories import UserFactory

from ..monitorings.factories import MonitoringFactory
from .factories import GlobalTagFactory, TagFactory


class ObjectMixin:
    def setUp(self):
        self.user = UserFactory(username="john")
        self.tag = TagFactory()
        self.monitoring = self.permission_object = self.tag.monitoring


class TagListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_tag"]

    def get_url(self):
        return reverse("cases_tags:list", kwargs={"monitoring": self.monitoring.pk})


class TagDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_tag"]

    def get_url(self):
        return self.tag.get_absolute_url()


class TagCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_tag"]

    def get_url(self):
        return reverse("cases_tags:create", kwargs={"monitoring": self.monitoring.pk})

    def test_create(self):
        self.grant_permission()
        self.client.login(username="john", password="pass")
        self.client.post(self.get_url(), {"name": "test"})


class TagUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_tag"]

    def get_url(self):
        return reverse(
            "cases_tags:update",
            kwargs={"monitoring": self.monitoring.pk, "pk": self.tag.pk},
        )


class TagDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.delete_tag"]

    def get_url(self):
        return reverse(
            "cases_tags:delete",
            kwargs={"monitoring": self.monitoring.pk, "pk": self.tag.pk},
        )


class TagAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.monitoring = MonitoringFactory()

    def test_filter_by_name(self):
        TagFactory(monitoring=self.monitoring, name="123")
        TagFactory(monitoring=self.monitoring, name="456")
        resp = self.client.get(
            path=reverse(
                "cases_tags:autocomplete",
                kwargs={"monitoring": str(self.monitoring.pk)},
            ),
            data={"q": "123"},
        )

        self.assertContains(resp, "123")
        self.assertNotContains(resp, "456")

    def test_get_result_label_without_case(self):
        GlobalTagFactory(name="123")
        resp = self.client.get(
            path=reverse(
                "cases_tags:autocomplete",
                kwargs={"monitoring": str(self.monitoring.pk)},
            ),
            data={"q": "123"},
        )
        self.assertContains(resp, "123 (0)")

    def test_get_result_label_with_case(self):
        CaseFactory(tags=[TagFactory(monitoring=self.monitoring, name="123")])

        resp = self.client.get(
            path=reverse(
                "cases_tags:autocomplete",
                kwargs={"monitoring": str(self.monitoring.pk)},
            ),
            data={"q": "123"},
        )
        self.assertContains(resp, "123 (1)")

    def test_filter_by_monitoring(self):
        valid_tag = TagFactory(monitoring=self.monitoring)
        invalid_tag = TagFactory(monitoring=MonitoringFactory())
        global_tag = TagFactory(monitoring=None)

        resp = self.client.get(
            path=reverse(
                "cases_tags:autocomplete",
                kwargs={"monitoring": str(self.monitoring.pk)},
            )
        )
        self.assertContains(resp, valid_tag.name)
        self.assertNotContains(resp, invalid_tag.name)
        self.assertContains(resp, global_tag.name)
