from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase

from feder.main.mixins import PermissionStatusMixin
from feder.users.factories import UserFactory
from .factories import AlertFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username="john")
        self.alert = AlertFactory()
        self.monitoring = self.permission_object = self.alert.monitoring


class AlertListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.view_alert', ]

    def get_url(self):
        return reverse('alerts:list', kwargs={"monitoring": self.monitoring.pk})


class AlertDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.view_alert', ]

    def get_url(self):
        return self.alert.get_absolute_url()


class AlertCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('alerts:create', kwargs={"monitoring": self.monitoring.pk})


class AlertUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_alert', ]

    def get_url(self):
        return reverse('alerts:update', kwargs={'pk': self.alert.pk})


class AlertDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_alert', ]

    def get_url(self):
        return reverse('alerts:delete', kwargs={'pk': self.alert.pk})

    def test_save(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        self.client.post(self.get_url(), {'reason': 'test'})


class AlertStatusViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_alert', ]

    def get_url(self):
        return reverse('alerts:status', kwargs={'pk': self.alert.pk})

    def test_status_action(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        self.client.post(self.get_url())
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.solver, self.user)
        self.assertEqual(self.alert.status, True)
        self.client.post(self.get_url(), {})
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, False)

