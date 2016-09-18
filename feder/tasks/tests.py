from django.core.urlresolvers import reverse
from django.test import TestCase

from feder.main.mixins import PermissionStatusMixin
from feder.users.factories import UserFactory

from .factories import TaskFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.task = TaskFactory()
        self.permission_object = self.task.case.monitoring


class CaseTestCase(ObjectMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        response = self.client.get(self.task.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class TaskCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_task', ]

    def get_url(self):
        return reverse('tasks:create', kwargs={'case': str(self.task.case.pk)})


class TaskUpdateViewPermTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_task', ]

    def get_url(self):
        return reverse('tasks:update', kwargs={'pk': self.task.pk})


class TaskDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_task', ]
    template_name = 'tasks/task_confirm_delete.html'

    def get_url(self):
        return reverse('tasks:delete', kwargs={'pk': self.task.pk})


class SitemapTestCase(ObjectMixin, TestCase):
    def test_letters(self):
        url = reverse('sitemaps', kwargs={'section': 'tasks'})
        response = self.client.get(url)
        self.assertContains(response, self.task.get_absolute_url())
