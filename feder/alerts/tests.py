from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase

from feder.monitorings.factory import factory_monitoring

from .models import Alert

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class SetUpMixin(object):
    def setUp(self):
        self.user = User.objects.create_user(username="john", password="top_secret")
        self.quest = User.objects.create_user(username="quest", password="top_secret")
        self.monitoring = factory_monitoring(self.user)
        self.alert = Alert.objects.create(reason="lorem",
                                          author=self.user,
                                          monitoring=self.monitoring)


class PermCheckMixin(SetUpMixin):
    anonymous_status = 302
    non_permitted_status = 403
    permitted_status = 200

    def login(self):
        self.client.login(username="quest", password="top_secret")

    def login_permitted(self):
        self.client.login(username="john", password="top_secret")

    def test_user_anonymous(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.anonymous_status)

    def test_user_non_permitted(self):
        self.login()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.non_permitted_status)

    def test_user_permitted(self):
        self.login_permitted()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.permitted_status)


class ListPermTestCase(PermCheckMixin, TestCase):
    def get_url(self):
        return reverse('alerts:list', kwargs={"monitoring": self.monitoring.pk})


class DetailsPermTestCase(PermCheckMixin, TestCase):
    def get_url(self):
        return self.alert.get_absolute_url()


class CreatePermTestCase(PermCheckMixin, TestCase):
    anonymous_status = 200
    non_permitted_status = 200

    def get_url(self):
        return reverse('alerts:create', kwargs={"monitoring": self.monitoring.pk})


class UpdatePermTestCase(PermCheckMixin, TestCase):
    def get_url(self):
        return reverse('alerts:update', kwargs={"pk": self.alert.pk})


class SwitchPermTestCase(PermCheckMixin, TestCase):
    def get_url(self):
        return reverse('alerts:status', kwargs={"pk": self.alert.pk})
