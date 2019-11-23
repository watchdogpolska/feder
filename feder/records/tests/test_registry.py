from django.template import loader
from django.test import TestCase

from feder.letters.factories import IncomingLetterFactory
from feder.records.registry import record_type_registry


class LetterTypeTestCase(TestCase):
    def setUp(self):
        self.registry = record_type_registry
        self.object = IncomingLetterFactory()

    def test_verbose_name_is_not_empty(self):
        self.assertTrue(
            self.registry.get_type(self.object).get_verbose_name(self.object)
        )

    def test_verbose_name_plural_is_string(self):
        self.assertTrue(
            self.registry.get_type(self.object).get_verbose_name_plural(self.object)
        )

    def test_template_milestone_item_exists(self):
        loader.get_template(
            self.registry.get_type(self.object).get_template_milestone_item()
        )

    def test_template_milestone_item_renders(self):
        template = loader.get_template(
            self.registry.get_type(self.object).get_template_milestone_item()
        )
        self.assertTrue(template.render({"object": self.object}))

    def test_template_content_item_exists(self):
        loader.get_template(
            self.registry.get_type(self.object).get_template_content_item()
        )

    def test_template_content_item_renders(self):
        template = loader.get_template(
            self.registry.get_type(self.object).get_template_content_item()
        )
        self.assertTrue(template.render({"object": self.object}))
