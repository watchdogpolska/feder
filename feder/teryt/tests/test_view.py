from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase

from feder.teryt import views
from feder.teryt.factory import JSTFactory


class TerytViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.jst = JSTFactory()

    def test_list_display(self):
        request = self.factory.get(reverse('teryt:list'))
        response = views.JSTListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        request = self.factory.get(self.jst.get_absolute_url())
        response = views.JSTDetailView.as_view()(request, slug=self.jst.slug)
        self.assertEqual(response.status_code, 200)
