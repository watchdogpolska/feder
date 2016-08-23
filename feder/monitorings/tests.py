from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.monitorings.models import Monitoring
from feder.users.factories import UserFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.monitoring = Monitoring.objects.create(name="Lor", user=self.user)


class MonitoringCreateViewTestCase(ObjectMixin, TestCase):
    def test_perm_anonymouse(self):
        response = self.client.get(reverse('monitorings:create'))
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(reverse('monitorings:create'))
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        assign_perm('monitorings.add_monitoring', self.user)
        self.client.login(username='john', password='pass')
        response = self.client.get(reverse('monitorings:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")


class MonitoringListViewTestCase(ObjectMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse('monitorings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)


class MonitoringDetailViewTestCase(ObjectMixin, TestCase):
    def test_details_display(self):
        response = self.client.get(self.monitoring.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)


class MonitoringUpdateViewTestCase(ObjectMixin, TestCase):
    def get_url(self):
        return reverse('monitorings:update', kwargs={'slug': self.monitoring.slug})

    def test_perm_anonymouse(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        assign_perm('monitorings.change_monitoring', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")


class MonitoringDeleteViewTestCase(ObjectMixin, TestCase):
    def get_url(self):
        return reverse('monitorings:delete', kwargs={'slug': self.monitoring.slug})

    def test_perm_anonymouse(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        assign_perm('monitorings.delete_monitoring', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "monitorings/monitoring_confirm_delete.html")


class PermissionWizardTestCase(ObjectMixin, TestCase):
    def get_url(self):
        return reverse('monitorings:perm-add', kwargs={'slug': self.monitoring.slug})

    def test_perm_anonymouse(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        assign_perm('monitorings.manage_perm', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitorings/permission_wizard.html')


class MonitoringPermissionViewTestCase(ObjectMixin, TestCase):
    def get_url(self):
        return reverse('monitorings:perm', kwargs={'slug': self.monitoring.slug})

    def test_perm_anonymouse(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        assign_perm('monitorings.manage_perm', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitorings/monitoring_permissions.html')


class MonitoringUpdatePermissionViewTestCase(ObjectMixin, TestCase):
    def get_url(self):
        return reverse('monitorings:perm-update', kwargs={'slug': self.monitoring.slug,
                       'user_pk': self.user.pk})

    def test_perm_anonymouse(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        assign_perm('monitorings.manage_perm', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitorings/monitoring_form.html')
