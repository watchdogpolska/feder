from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.cases.models import Case
from feder.institutions.factory import factory_institution
from feder.monitorings.models import Monitoring
from feder.questionaries.models import Questionary
from feder.tasks.models import Task

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class SetUpMixin(object):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user', email='jacob@example.com', password='top_secret')
        assign_perm('monitorings.add_monitoring', self.user)
        self.quest = User.objects.create_user(
            username='quest', email='smith@example.com', password='top_secret')
        self.monitoring = Monitoring(name="Lor", user=self.user)
        self.monitoring.save()
        self.questionary = Questionary(title="blabla", monitoring=self.monitoring)
        self.questionary.save()
        self.institution = factory_institution(self.user)
        self.case = Case(name="blabla",
                         monitoring=self.monitoring,
                         institution=self.institution,
                         user=self.user)
        self.case.save()
        self.task = Task(case=self.case, questionary=self.questionary)
        self.task.save()


class CaseTestCase(SetUpMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        response = self.client.get(self.task.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class PermCheckMixin(SetUpMixin):
    url = None
    template_name = 'tasks/task_form.html'
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


class CreateViewPermTestCase(PermCheckMixin, TestCase):
    def _get_url(self):
        return reverse('tasks:create', kwargs={'case': str(self.case.pk)})


class UpdateViewPermTestCase(PermCheckMixin, TestCase):
    def _get_url(self):
        return reverse('tasks:update', kwargs={'pk': self.task.pk})


class DeleteViewPermTestCase(PermCheckMixin, TestCase):
    template_name = 'tasks/task_confirm_delete.html'

    def _get_url(self):
        return reverse('tasks:delete', kwargs={'pk': self.task.pk})
