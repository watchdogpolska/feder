from django.test import TestCase
from django.urls import reverse
from ..serializers import RecordSerializer
from ..factories import RecordFactory
from ...letters.factories import IncomingLetterFactory

class ReadOnlyViewSetMixin:
    basename = None
    serializer_class = None
    factory_class = None
    pk_field = "pk"

    def setUp(self):
        if not self.factory_class:
            raise NotImplementedError("factory_class must be defined")
        self.obj = self.factory_class()

    def get_extra_kwargs(self):
        return dict()

    def get_url(self, name, **kwargs):
        if not self.basename:
            raise NotImplementedError("get_url must be overridden or basename defined")
        return reverse("{}-{}".format(self.basename, name), kwargs=kwargs)

    def get_url_list(self):
        return self.get_url(name="list", **self.get_extra_kwargs())

    def test_list_plain(self):
        response = self.client.get(self.get_url_list())
        results = response.json()["results"]
        self.validate_item(
            next(obj for obj in results if obj[self.pk_field] == self.obj.pk)
        )

    def get_url_detail(self):
        return self.get_url(name="detail", **self.get_extra_kwargs(), pk=self.obj.pk)

    def test_retrieve_plain(self):
        response = self.client.get(self.get_url_detail())
        self.assertEqual(response.status_code, 200)
        self.validate_item(response.json())

    def validate_item(self, item):
        raise NotImplementedError("validate_item must be overridden")

class RecordViewSetTestCase(ReadOnlyViewSetMixin, TestCase):
    basename = "record"
    serializer_class = RecordSerializer
    factory_class = RecordFactory

    def validate_item(self, item):
        self.assertEqual(item[self.pk_field], self.obj.pk)

class RecordLetterViewSetTestCase(ReadOnlyViewSetMixin, TestCase):
    basename = "record"
    serializer_class = RecordSerializer
    factory_class = RecordFactory

    def setUp(self):
        super().setUp()
        self.letter = IncomingLetterFactory(record=self.obj)

    def validate_item(self, item):
        self.assertEqual(item[self.pk_field], self.obj.pk)
        self.assertEqual(item["content_object"]["title"], self.letter.title)

