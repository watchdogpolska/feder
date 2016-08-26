from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from .models import Alert
from feder.main.mixins import PermissionStatusMixin


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username="john", password="pass")
        self.monitoring = self.permission_object = MonitoringFactory(user=self.user)
        self.alert = Alert.objects.create(reason="lorem",
                                          author=self.user,
                                          monitoring=self.monitoring)


class AlertListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.view_alert', ]

    def get_url(self):
        return reverse('alerts:list', kwargs={"monitoring": self.monitoring.pk})


class AlertDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.view_alert', ]

    def get_url(self):
        return self.alert.get_absolute_url()


class AlertCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
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


class AlertStatusViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_alert', ]

    def get_url(self):
        return reverse('alerts:status', kwargs={'pk': self.alert.pk})
