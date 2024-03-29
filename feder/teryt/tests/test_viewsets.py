from django.test import RequestFactory, TestCase
from teryt_tree.rest_framework_ext.viewsets import JednostkaAdministracyjnaViewSet

from feder.teryt.factories import JSTFactory


class TerytViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.jst = JSTFactory()

    def test_list_display(self):
        request = self.factory.get("/")
        view_func = JednostkaAdministracyjnaViewSet.as_view({"get": "list"})
        response = view_func(request)
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        request = self.factory.get("/")
        view_func = JednostkaAdministracyjnaViewSet.as_view({"get": "retrieve"})
        response = view_func(request, pk=self.jst.pk)
        self.assertEqual(response.status_code, 200)
