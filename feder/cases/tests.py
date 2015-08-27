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
from feder.teryt.models import JednostkaAdministracyjna

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class CasesTestCase(TestCase):

    def _get_third_level_jst(self):
        jst = AutoFixture(JednostkaAdministracyjna,
                          field_values={'updated_on': '2015-02-12'},
                          generate_fk=True).create_one(commit=False)
        jst.save()
        JednostkaAdministracyjna.objects.rebuild()
        return jst

    def _get_institution(self):
        jst = self._get_third_level_jst()
        institution = AutoFixture(Institution,
                                  field_values={'user': self.user, 'jst': jst},
                                  generate_fk=True).create_one()
        return institution

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        assign_perm('monitorings.add_monitoring', self.user)
        self.quest = User.objects.create_user(
            username='smith', email='smith@example.com', password='top_secret')
        self.monitoring = Monitoring(name="Lor", user=self.user)
        self.monitoring.save()
        self.questionary = Questionary(title="blabla", monitoring=self.monitoring)
        self.questionary.save()
        self.institution = self._get_institution()
        self.case = Case(name="blabla", monitoring=self.monitoring,
                         institution=self.institution,
                         user=self.user)
        self.case.save()

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

    def test_create_permission_check(self):
        self._perm_check(views.CaseCreateView.as_view(), 'cases:create',
                         kwargs={'monitoring': str(self.case.pk)})

    def test_update_permission_check(self):
        self._perm_check(views.CaseUpdateView.as_view(), 'cases:update',
                         kwargs={'slug': self.case.slug})

    def test_delete_permission_check(self):
        self._perm_check(views.CaseDeleteView.as_view(), 'cases:delete',
                         kwargs={'slug': self.case.slug})
