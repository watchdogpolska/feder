from autofixture import AutoFixture
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase

from feder.teryt import views
from feder.teryt.models import JednostkaAdministracyjna


class TerytViewTestCase(TestCase):
    def _get_third_level_jst(self):
        jst = AutoFixture(JednostkaAdministracyjna,
            field_values={'updated_on': '2015-02-12', 'rght': 0},
            generate_fk=True).create_one()
        JednostkaAdministracyjna.objects.rebuild()
        return jst

    def setUp(self):
        self.factory = RequestFactory()
        self.jst = self._get_third_level_jst()

    def test_list_display(self):
        request = self.factory.get(reverse('teryt:list'))
        response = views.JednostkaAdministracyjnaListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        request = self.factory.get(self.jst.get_absolute_url())
        response = views.JSTDetailView.as_view()(request, slug=self.jst.slug)
        self.assertEqual(response.status_code, 200)
