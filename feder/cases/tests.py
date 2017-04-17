from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase

from feder.institutions.factories import InstitutionFactory
from feder.main.mixins import PermissionStatusMixin
from feder.users.factories import UserFactory
from .factories import CaseFactory
from .forms import CaseForm
from .views import CaseAutocomplete


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username="john")
        self.case = CaseFactory()
        self.permission_object = self.case.monitoring


class CaseFormTestCase(ObjectMixin, TestCase):
    def test_standard_save(self):
        data = {'name': 'example',
                'institution': InstitutionFactory().pk}
        form = CaseForm(monitoring=self.case.monitoring,
                        user=self.user,
                        data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        obj = form.save()
        self.assertEqual(obj.name, "example")
        self.assertEqual(obj.monitoring, self.case.monitoring)
        self.assertEqual(obj.user, self.user)


class CaseListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('cases:list')


class CaseDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
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


class CaseAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_by_name(self):
        CaseFactory(name='123')
        CaseFactory(name='456')
        request = self.factory.get('/customer/details', data={'q': '123'})
        response = CaseAutocomplete.as_view()(request)
        self.assertContains(response, '123')
        self.assertNotContains(response, '456')


class SitemapTestCase(ObjectMixin, TestCase):
    def test_cases(self):
        url = reverse('sitemaps', kwargs={'section': 'cases'})
        needle = reverse('cases:details', kwargs={'slug': self.case.slug})
        response = self.client.get(url)
        self.assertContains(response, needle)
