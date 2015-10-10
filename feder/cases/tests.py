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

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class SetUpMixin(object):
    def _get_institution(self):
        jst = JSTFactory()
        institution = AutoFixture(Institution,
                                  field_values={'user': self.user, 'jst': jst},
                                  generate_fk=True).create_one()
        return institution

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='user', email='jacob@example.com', password='top_secret')
        assign_perm('monitorings.add_monitoring', self.user)
        self.quest = User.objects.create_user(
            username='quest', email='smith@example.com', password='top_secret')
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

        request.user = self.quest
        with self.assertRaises(PermissionDenied):
            view(request, **kwargs)


class PermCheckMixin(SetUpMixin):
    url = None
    contains = False
    template_name = 'cases/case_form.html'
    perm = None
    anonymous_user_status = 302
    non_permitted_status = 403
    permitted_status = 200

    def login(self):
        self.client.login(username='quest', password='top_secret')

    def login_permitted(self):
        self.client.login(username='user', password='top_secret')

    def _get_url(self):
        return self.url

    def test_anonymous_user(self):
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.anonymous_user_status)

    def test_non_permitted_user(self):
        self.login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.non_permitted_status)

    def test_permitted_user(self):
        self.login_permitted()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.permitted_status)
        self.assertTemplateUsed(response, self.template_name)
        if self.contains:
            self.assertContains(response, self.institution.name)


class CreateViewPermCheck(PermCheckMixin, TestCase):
    def _get_url(self):
        return reverse('cases:create', kwargs={'monitoring': str(self.monitoring.pk)})


class UpdateViewPermCheck(PermCheckMixin, TestCase):
    def _get_url(self):
        return reverse('cases:update', kwargs={'slug': self.case.slug})


class DeleteViewPermCheck(PermCheckMixin, TestCase):
    template_name = 'cases/case_confirm_delete.html'

    def _get_url(self):
        return reverse('cases:delete', kwargs={'slug': self.case.slug})
