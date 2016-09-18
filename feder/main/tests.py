from django.core.urlresolvers import reverse
from django.test import TestCase


class HomeViewTestCase(TestCase):
    def test_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class SitemapTestCase(TestCase):
    def test_main(self):
        url = reverse('sitemaps', kwargs={'section': 'main'})
        self.assertEqual(self.client.get(url).status_code, 200)
