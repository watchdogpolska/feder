from io import StringIO

from django.test import TestCase
from ..letters.factories import IncomingLetterFactory, AttachmentFactory
from .tasks import index_letter
from time import sleep
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.query import MultiMatch, Match, Q, MoreLikeThis
from elasticsearch_dsl.connections import get_connection, connections
from .documents import LetterDocument
from django.core.management import call_command
import time
from collections.abc import Iterable
from .queries import more_like_this, search_keywords


class ESMixin:
    connection_alias = "default"

    def setUp(self):
        super().setUp()
        es = get_connection()
        for index in es.indices.get_alias("*").keys():
            Search.from_dict({"query": {"match_all": {}}}).index(index).delete()

    def refresh_all(self):
        for index in get_connection().indices.get_alias("*").keys():
            Index(index).refresh()

    def assertMatch(self, result, items):
        items = items if isinstance(items, Iterable) else [items]
        self.assertEqual(len(result), len(items))
        for obj in items:
            self.assertTrue(any(x.title == obj.title for x in result))

    def index(self, items):
        items = items if isinstance(items, Iterable) else [items]
        index_letter.now([x.pk for x in items])
        self.refresh_all()


class IndexLetterTestCase(ESMixin, TestCase):
    def test_single_letter_index(self):
        letter = IncomingLetterFactory()
        self.index(letter)
        result = search_keywords(letter.title)

        self.assertMatch(result, letter)

    def test_attachment_letter_index(self):
        attachment = AttachmentFactory()
        letter = attachment.letter
        self.index(letter)

        result = search_keywords(letter.title)

        self.assertMatch(result, letter)

    def test_search_by_attachment_content(self):
        attachment = AttachmentFactory(attachment__text="hello world")
        letter = attachment.letter
        self.index(letter)

        result = search_keywords("hello")

        self.assertMatch(result, letter)

    def test_search_by_title(self):
        letter = IncomingLetterFactory(body="hello world")
        self.index(letter)

        result = search_keywords("hello")

        self.assertMatch(result, letter)

    def test_search_more_like_this_by_title(self):
        letter_a = IncomingLetterFactory(title="hello world bla bla")
        letter_b = IncomingLetterFactory(title="hello world bla bla")
        self.index([letter_a, letter_b])

        doc = LetterDocument.get(letter_a.pk)
        result = more_like_this(doc)

        self.assertMatch(result, letter_b)

    def test_search_more_like_this_by_attachment(self):
        text = "hello world bla bla"
        letter_a = AttachmentFactory(attachment__text=text).letter
        letter_b = AttachmentFactory(attachment__text=text).letter
        self.index([letter_a, letter_b])

        doc = LetterDocument.get(letter_a.pk)
        result = more_like_this(doc)

        self.assertMatch(result, letter_b)


class IndexCommandTestCase(ESMixin, TestCase):
    def test_single_letter_index(self):
        letter = IncomingLetterFactory()
        call_command("es_index", "--skip-queue", stdout=StringIO())
        self.refresh_all()

        result = search_keywords(letter.title)

        self.assertMatch(result, letter)
