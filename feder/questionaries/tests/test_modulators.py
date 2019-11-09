from datetime import date

from django.forms.fields import Field
from django.test import TestCase
from django.utils import six

from feder.teryt.factories import JSTFactory
from feder.teryt.models import JST
from ..forms import QuestionDefinitionForm
from ..models import Question
from ..modulator import (
    CharModulator,
    ChoiceModulator,
    DateModulator,
    EmailModulator,
    IntegerModulator,
    JSTModulator,
    LetterChoiceModulator,
)
from ...tasks.forms import AnswerForm


class ModulatorMixin:
    answer_text_cls = (str,)

    def setUp(self):
        self.question = Question(genre=self.tested_cls.name)
        self.question.definition = self._get_mock_definition()
        self.content = self.get_mock_content()

    def _get_mock_definition(self):
        form = QuestionDefinitionForm(instance=self.question, data=self.CREATE_INPUT)
        msg = "CREATE_INPUT in {name} is invalid. {errors}".format(
            name=self.__class__.__name__, errors=form.errors
        )
        self.assertTrue(form.is_valid(), msg=msg)
        return form.cleaned_data

    def get_mock_content(self):
        form = AnswerForm(question=self.question, data=self.SUBMIT_INPUT)
        msg = "SUBMIT_INPUT in {name} is invalid. {errors}".format(
            name=self.__class__.__name__, errors=form.errors
        )
        self.assertTrue(form.is_valid(), msg=msg)
        return form.modulator.get_content(form.question.definition, form.cleaned_data)

    def test_list_create_question_fields(self):
        """Tests data format in list_create_question_fields.
        """
        for name, field in self.tested_cls().list_create_question_fields():
            self.assertIsInstance(name, (str,))
            self.assertIsInstance(field, Field)

    def test_list_create_answer_fields(self):
        for name, field in self.tested_cls().list_create_answer_fields(
            self.question.definition
        ):
            self.assertIsInstance(name, (str,))
            self.assertIsInstance(field, Field)

    def test_get_label_text(self):
        label = self.tested_cls().get_label_text(self.question.definition)
        self.assertIsInstance(label, (str,))

    def test_get_answer_text(self,):
        text = self.tested_cls().get_answer_text(self.question.definition, self.content)
        self.assertIsInstance(text, self.answer_text_cls)

    def test_get_label_column(self):
        columns = self.tested_cls().get_label_column(self.question.definition)
        self.assertTrue(len(columns) > 0)

    def test_get_answer_columns(self):
        rows = self.tested_cls().get_answer_columns(
            self.question.definition, self.content
        )
        self.assertTrue(len(rows) > 0)

    def test_get_kwargs_without_defined_question(self):
        self.question.modulator.get_kwargs({})


class CharModulatorTestCase(TestCase):
    CREATE_INPUT = {
        "comment": False,
        "comment_help": "xxxx",
        "comment_label": "",
        "comment_required": False,
        "help_text": "chyba tak",
        "name": "pole tekstowe",
        "required": False,
    }
    SUBMIT_INPUT = {"value": "abc"}
    tested_cls = CharModulator


class IntegerModulatorTestCase(ModulatorMixin, TestCase):
    CREATE_INPUT = {"help_text": "Some help text", "name": "Some title"}
    SUBMIT_INPUT = {"value": "250"}
    tested_cls = IntegerModulator


class EmailModulatorTestCase(ModulatorMixin, TestCase):
    CREATE_INPUT = {"help_text": "Some help text", "name": "Some title"}
    SUBMIT_INPUT = {"value": "xx@aa.pl"}
    tested_cls = EmailModulator


class DateModulatorTestCase(ModulatorMixin, TestCase):
    CREATE_INPUT = {"help_text": "Some help text", "name": "Some title"}
    SUBMIT_INPUT = {"value": "2015-11-11"}
    tested_cls = DateModulator
    answer_text_cls = date


class ChoiceModulatorTestCase(ModulatorMixin, TestCase):
    CREATE_INPUT = {"help_text": "Some help text", "name": "Some title", "choices": "x"}
    SUBMIT_INPUT = {"value": 0}
    tested_cls = ChoiceModulator


class JSTModulatorTestCase(ModulatorMixin, TestCase):
    CREATE_INPUT = {"help_text": "Some help text", "name": "Some title", "area": "all"}
    SUBMIT_INPUT = {"value": 25}
    tested_cls = JSTModulator
    answer_text_cls = JST

    def setUp(self):
        self.jst = JSTFactory(pk=25)
        super().setUp()


class LetterChoiceModulatorTestCase(ModulatorMixin, TestCase):
    CREATE_INPUT = {
        "help_text": "Some help text",
        "name": "Some title",
        "filter": "all",
    }
    SUBMIT_INPUT = {}
    tested_cls = LetterChoiceModulator
