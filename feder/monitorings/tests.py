from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from formtools.utils import form_hmac
from guardian.shortcuts import assign_perm

from feder.institutions.factory import factory_institution
from feder.letters.models import Letter
from feder.monitorings.forms import CreateMonitoringForm
from feder.monitorings.models import Monitoring

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class SetUpMixin(object):
    monitoring_create = True

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        assign_perm('monitorings.add_monitoring', self.user)
        self.quest = User.objects.create_user(
            username='smith', email='smith@example.com', password='top_secret')
        if self.monitoring_create:
            self.monitoring = Monitoring.objects.create(name="Lor", user=self.user)


class PermissionTestMixin(SetUpMixin):
    url = None
    template_name = 'monitorings/monitoring_form.html'
    contains = True

    def get_url(self):
        return self.url

    def test_anonymous_user(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_non_permitted_user(self):
        self.client.login(username='smith', password='top_secret')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_permitted_user(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        if self.contains:
            self.assertContains(response, self.monitoring)


class MonitoringTestCase(SetUpMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse('monitorings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_details_display(self):
        response = self.client.get(self.monitoring.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)


class UpdateViewPermTestCase(PermissionTestMixin, TestCase):
    def get_url(self):
        return reverse('monitorings:update', kwargs={'slug': self.monitoring.slug})


class DeleteViewPermTestCase(PermissionTestMixin, TestCase):
    template_name = 'monitorings/monitoring_confirm_delete.html'

    def get_url(self):
        return reverse('monitorings:delete', kwargs={'slug': self.monitoring.slug})


class CreateViewPermTestCase(PermissionTestMixin, TestCase):
    url = reverse('monitorings:create')
    contains = False


class PermissionWizardPermTestCase(PermissionTestMixin, TestCase):
    template_name = 'monitorings/permission_wizard.html'

    def get_url(self):
        return reverse('monitorings:perm-add', kwargs={'slug': self.monitoring.slug})


class MonitoringPermissionViewPermTestCase(PermissionTestMixin, TestCase):
    template_name = 'monitorings/monitoring_permissions.html'

    def get_url(self):
        return reverse('monitorings:perm', kwargs={'slug': self.monitoring.slug})


class MonitoringUpdatePermissionView(PermissionTestMixin, TestCase):
    template_name = 'monitorings/monitoring_form.html'

    def get_url(self):
        return reverse('monitorings:perm-update', kwargs={'slug': self.monitoring.slug,
                       'user_pk': self.user.pk})


class MonitoringAddViewTestCase(SetUpMixin, TestCase):
    monitoring_create = False

    def test_create(self):
        institution = factory_institution(self.user)
        param = {'text': 'Example text {{EMAIL}}',
                 'recipients': [institution.pk],
                 'name': 'Example name'}
        assign_perm('monitorings.add_monitoring', self.user)

        self.client.login(username='jacob', password='top_secret')
        response = self.client.post(reverse('monitorings:create'), param)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Monitoring.objects.count(), 0)

        security = form_hmac(CreateMonitoringForm(param))
        param.update({'stage': 2, 'hash': security})
        response = self.client.post(reverse('monitorings:create'), param)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Monitoring.objects.count(), 1)

        self.assertEqual(len(mail.outbox), 1)

        Letter.objects.get().eml.delete()

