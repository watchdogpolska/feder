from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from django.core.exceptions import PermissionDenied
from . import views

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class MonitoringTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        self.quest = User.objects.create_user(
            username='smith', email='smith@example.com', password='top_secret')
        self.monitoring = Monitoring(name="Lor", user=self.user)
        self.monitoring.save()

    def test_details_display(self):
        request = self.factory.get(self.monitoring.get_absolute_url())
        request.user = self.user
        response = views.MonitoringDetailView.as_view()(request, slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 200)

    def test_create_permission_check(self):
        request = self.factory.get(reverse('monitorings:create'))
        request.user = self.user
        response = views.MonitoringCreateView.as_view()(request, slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        response = views.MonitoringCreateView.as_view()(request, slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 200)

    def test_update_permission_check(self):
        request = self.factory.get(reverse('monitorings:update',
            kwargs={'slug': self.monitoring.slug}))
        request.user = self.user
        response = views.MonitoringUpdateView.as_view()(request, slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        response = views.MonitoringUpdateView.as_view()(request, slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 403)

    def test_delete_permission_check(self):
        request = self.factory.get(reverse('monitorings:delete',
            kwargs={'slug': self.monitoring.slug}))
        request.user = self.user
        response = views.MonitoringDeleteView.as_view()(request, slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        with self.assertRaise(PermissionDenied):
            views.MonitoringDeleteView.as_view()(request, slug=self.monitoring.slug)
