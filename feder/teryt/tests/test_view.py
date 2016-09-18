from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase

from feder.teryt import views
from feder.teryt.factories import JSTFactory
from django.core.urlresolvers import reverse_lazy


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


class JSTDetailViewTestCase(TestCase):
    def setUp(self):
        self.object = JSTFactory()
        self.url = self.object.get_absolute_url()

    def test_template_used(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'teryt/jst_detail.html')

    def test_contains_name(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, self.object.name)


class JSTListViewTestCase(TestCase):
    url = reverse_lazy('teryt:list')

    def setUp(self):
        self.object = JSTFactory()
        self.object_list = JSTFactory.create_batch(size=25, parent=self.object)

    def test_template_used(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'teryt/jst_list.html')

    def test_contains_name(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, self.object.name)
        self.assertContains(resp, self.object_list[0].name)


class SitemapTestCase(TestCase):
    def setUp(self):
        self.teryt = JSTFactory()

    def test_letters(self):
        url = reverse('sitemaps', kwargs={'section': 'teryt'})
        response = self.client.get(url)
        self.assertContains(response, self.teryt.get_absolute_url())
