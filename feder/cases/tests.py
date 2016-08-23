from autofixture import AutoFixture
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from guardian.shortcuts import assign_perm

from feder.cases import views
from feder.cases.models import Case
from feder.institutions.models import Institution
from feder.monitorings.models import Monitoring
from feder.questionaries.models import Questionary
from feder.teryt.factories import JSTFactory
from feder.users.factories import UserFactory


class SetUpMixin(object):
    def _get_institution(self):
        jst = JSTFactory()
        institution = AutoFixture(Institution,
                                  field_values={'user': self.user, 'jst': jst},
                                  generate_fk=True).create_one()
        return institution

    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory(username="john")
        self.monitoring = Monitoring.objects.create(name="Lor", user=self.user)
        self.institution = self._get_institution()
        self.case = Case.objects.create(name="blabla",
                                        monitoring=self.monitoring,
                                        institution=self.institution,
                                        user=self.user)


class CasesTestCase(SetUpMixin, TestCase):

    def test_list_display(self):
        request = self.factory.get(reverse('cases:list'))
        response = views.CaseListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        request = self.factory.get(self.case.get_absolute_url())
        request.user = self.user
        response = views.CaseDetailView.as_view()(request, pk=self.case.pk)
        self.assertEqual(response.status_code, 200)

    def _perm_check(self, view, reverse_name, kwargs):
        request = self.factory.get(reverse(reverse_name,
                                           kwargs=kwargs))
        request.user = self.user
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)

        request.user = self.john
        with self.assertRaises(PermissionDenied):
            view(request, **kwargs)


class PermCheckMixin(SetUpMixin):
    template_name = 'cases/case_form.html'
    permission = []
    contains = True

    def get_url(self):
        return NotImplementedError()

    def test_anonymous_user(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        for perm in self.permission:
            assign_perm(perm, self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        if self.contains:
            self.assertContains(response, self.institution.name)


class CreateViewPermCheck(PermCheckMixin, TestCase):
    permission = ['monitorings.add_case', ]

    def get_url(self):
        return reverse('cases:create', kwargs={'monitoring': str(self.monitoring.pk)})


class UpdateViewPermCheck(PermCheckMixin, TestCase):
    permission = ['monitorings.change_case', ]

    def get_url(self):
        return reverse('cases:update', kwargs={'slug': self.case.slug})


class DeleteViewPermCheck(PermCheckMixin, TestCase):
    permission = ['monitorings.delete_case', ]
    template_name = 'cases/case_confirm_delete.html'
    contains = False

    def get_url(self):
        return reverse('cases:delete', kwargs={'slug': self.case.slug})
