from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.cases.models import Case
from feder.institutions.factories import factory_institution
from feder.monitorings.models import Monitoring
from feder.questionaries.models import Questionary
from feder.tasks.models import Task
from feder.users.factories import UserFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.monitoring = Monitoring.objects.create(name="Lor", user=self.user)
        self.questionary = Questionary.objects.create(title="blabla",
                                                      monitoring=self.monitoring)
        self.institution = factory_institution(self.user)
        self.case = Case.objects.create(name="blabla",
                                        monitoring=self.monitoring,
                                        institution=self.institution,
                                        user=self.user)
        self.task = Task.objects.create(case=self.case,
                                        questionary=self.questionary)


class CaseTestCase(ObjectMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        response = self.client.get(self.task.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class PermCheckMixin(ObjectMixin):
    url = None
    template_name = 'tasks/task_form.html'
    permission = []

    def get_url(self):
        raise NotImplementedError()

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


class CreateViewPermTestCase(PermCheckMixin, TestCase):
    permission = ['monitorings.add_task', ]

    def get_url(self):
        return reverse('tasks:create', kwargs={'case': str(self.case.pk)})


class UpdateViewPermTestCase(PermCheckMixin, TestCase):
    permission = ['monitorings.change_task', ]

    def get_url(self):
        return reverse('tasks:update', kwargs={'pk': self.task.pk})


class DeleteViewPermTestCase(PermCheckMixin, TestCase):
    permission = ['monitorings.delete_task', ]
    template_name = 'tasks/task_confirm_delete.html'

    def get_url(self):
        return reverse('tasks:delete', kwargs={'pk': self.task.pk})
