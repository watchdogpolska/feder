from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from feder.monitorings.factories import MonitoringFactory
from feder.cases.models import Case
from feder.users.factories import UserFactory
from feder.institutions.factories import InstitutionFactory
from feder.main.mixins import PermissionStatusMixin


class ObjectMixin(object):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory(username="john")
        self.monitoring = self.permission_object = MonitoringFactory(user=self.user)
        self.institution = InstitutionFactory()
        self.case = Case.objects.create(name="blabla",
                                        monitoring=self.monitoring,
                                        institution=self.institution,
                                        user=self.user)


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
        return reverse('cases:create', kwargs={'monitoring': str(self.monitoring.pk)})


class CaseUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_case', ]

    def get_url(self):
        return reverse('cases:update', kwargs={'slug': self.case.slug})


class CaseDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_case', ]

    def get_url(self):
        return reverse('cases:delete', kwargs={'slug': self.case.slug})
