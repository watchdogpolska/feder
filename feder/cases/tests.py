from django.core.urlresolvers import reverse
from django.test import TestCase
from feder.users.factories import UserFactory
from feder.main.mixins import PermissionStatusMixin
from .factories import CaseFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username="john")
        self.case = CaseFactory()
        self.permission_object = self.case.monitoring


class CaseListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('cases:list')


class CaseDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('cases:details', kwargs={'slug': self.case.slug})


class CaseCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_case', ]

    def get_url(self):
        return reverse('cases:create', kwargs={'monitoring': str(self.case.monitoring.pk)})


class CaseUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_case', ]

    def get_url(self):
        return reverse('cases:update', kwargs={'slug': self.case.slug})


class CaseDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_case', ]

    def get_url(self):
        return reverse('cases:delete', kwargs={'slug': self.case.slug})
