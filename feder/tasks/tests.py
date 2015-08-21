from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import assign_perm
from feder.teryt.models import JednostkaAdministracyjna, Category
from feder.institutions.models import Institution
from autofixture import AutoFixture
from feder.questionaries.models import Questionary
from feder.cases.models import Case
from feder.tasks.models import Task
from feder.tasks import views

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class CaseTestCase(TestCase):
    def _get_third_level_jst(self):
        jst = AutoFixture(JednostkaAdministracyjna,
            field_values={'updated_on': '2015-02-12'},
            generate_fk=True).create_one(commit=False)
        jst.rght = 0
        jst.save()
        return jst

    def _get_institution(self):
        jst = self._get_third_level_jst()
        institution = AutoFixture(Institution,
            field_values={'user': self.user, 'jst': jst}).create_one()
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
        self.task = Task(case=self.case, questionary=self.questionary)
        self.task.save()

    def test_details_display(self):
        request = self.factory.get(self.task.get_absolute_url())
        request.user = self.user
        response = views.TaskDetailView.as_view()(request, pk=self.task.pk)
        self.assertEqual(response.status_code, 200)

    def _perm_check(self, view, reverse_name, kwargs={}):
        request = self.factory.get(reverse(reverse_name,
            kwargs=kwargs))
        request.user = self.user
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        with self.assertRaises(PermissionDenied):
            response = view(request, **kwargs)

    def test_create_permission_check(self):
        self._perm_check(views.TaskCreateView.as_view(), 'tasks:create',
            kwargs={'case': str(self.case.pk)}
            )

    def test_update_permission_check(self):
        self._perm_check(views.TaskUpdateView.as_view(), 'tasks:update',
            kwargs={'pk': self.task.pk})

    def test_delete_permission_check(self):
        self._perm_check(views.TaskDeleteView.as_view(), 'tasks:delete',
            kwargs={'pk': self.task.pk})
