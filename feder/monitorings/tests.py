from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from guardian.shortcuts import assign_perm
from formtools.utils import form_hmac
from feder.institutions.factory import factory_institution
from feder.monitorings.forms import CreateMonitoringForm
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class PermissionTestMixin(object):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        self.quest = User.objects.create_user(
            username='smith', email='smith@example.com', password='top_secret')
        super(PermissionTestMixin, self).setUp()

    def _perm_check(self, url, template_name='monitorings/monitoring_form.html',
                    contains=True):
        self.client.login(username='smith', password='top_secret')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='jacob', password='top_secret')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        if contains:
            self.assertContains(response, self.monitoring)


class MonitoringTestCase(PermissionTestMixin, TestCase):
    def setUp(self):
        super(MonitoringTestCase, self).setUp()
        self.monitoring = Monitoring(name="Lor", user=self.user)
        self.monitoring.save()

    def test_list_display(self):
        response = self.client.get(reverse('monitorings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_details_display(self):
        response = self.client.get(self.monitoring.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_update_permission_check(self):
        self._perm_check(reverse('monitorings:update',
                                 kwargs={'slug': self.monitoring.slug}))

    def test_delete_permission_check(self):
        self._perm_check(reverse('monitorings:delete', kwargs={'slug': self.monitoring.slug}),
                         template_name='monitorings/monitoring_confirm_delete.html')


class MonitoringAddViewTestCase(PermissionTestMixin, TestCase):
    def test_create_permission_check(self):
        assign_perm('monitorings.add_monitoring', self.user)
        self._perm_check(reverse('monitorings:create'),
                         contains=False)

    def test_create(self):
        institution = factory_institution(self.user)
        param = {'text': 'Example text',
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
