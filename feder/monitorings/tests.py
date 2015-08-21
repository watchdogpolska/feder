from django.test import Client
from django.test import TestCase, RequestFactory
from feder.monitorings.models import Monitoring
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
        self.monitoring = Monitoring(name="Lor", user=self.user)
        self.monitoring.save()

    def test_details_display(self):
        request = self.factory.get(self.monitoring.get_absolute_url)
        request.user = self.user
        response = views.MonitoringDetailView.as_view(request)(slug=self.monitoring.slug)
        self.assertEqual(response.status_code, 200)
