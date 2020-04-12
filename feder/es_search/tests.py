from io import StringIO

from django.test import TestCase
from ..letters.factories import IncomingLetterFactory, AttachmentFactory
from .tasks import index_letter
from time import sleep
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.query import MultiMatch, Match, Q, MoreLikeThis
from elasticsearch_dsl.connections import get_connection, connections
from elasticsearch.exceptions import ElasticsearchException
from .documents import LetterDocument
from django.core.management import call_command
import time
from collections.abc import Iterable
from elasticsearch.exceptions import ConflictError
from .queries import more_like_this, search_keywords, find_document, delete_document
import time


class ESMixin:
    connection_alias = "default"
    index_delay = 10

    def setUp(self):
        super().setUp()
        for x in range(10):
            try:
                return LetterDocument.search().query().delete()
            except Exception:
                print("Sleep time for delete setUp")
                time.sleep(1)
                pass

    # def refresh_all(self):
    #     for index in get_connection().indices.get_alias("*").keys():
    #         Index(index).flush()
    #         Index(index).refresh()
    #         Index(index).clear_cache()
    #         Index(index).forcemerge()
    #         print(Index(index).stats())
    #     es = get_connection().health()
    #     time.sleep(self.index_delay)

    def assertMatch(self, result, items):
        items = items if isinstance(items, Iterable) else [items]
        self.assertEqual(len(result), len(items))
        for obj in items:
            self.assertTrue(any(x.title == obj.title for x in result))

    def index(self, items):
        items = items if isinstance(items, Iterable) else [items]
        pks = [x.pk for x in items]
        index_letter.now(pks)
        stop = True
        while stop:
            print("Delay for indexing")
            time.sleep(self.index_delay)
            for pk in pks:
                try:
                    if not find_document(pk):
                        break
                except ElasticsearchException as e:
                    print(e)
                    break
            else:
                stop = False


class IndexLetterTestCase(ESMixin, TestCase):
    text = "Lorem ipsum dolor sit amet consectetur adipiscing elit"

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
        attachment = AttachmentFactory(attachment__text=self.text)
        letter = attachment.letter
        self.index(letter)

        result = search_keywords("dolor")

        self.assertMatch(result, letter)

    def test_search_by_title(self):
        letter = IncomingLetterFactory(body=self.text)
        self.index(letter)

        result = search_keywords("dolor")

        self.assertMatch(result, letter)

    def test_search_more_like_this_by_title(self):
        letter_a = IncomingLetterFactory(title=self.text)
        letter_b = IncomingLetterFactory(title=self.text)
        self.index([letter_a, letter_b])

        doc = find_document(letter_a.pk)
        result = more_like_this(doc)

        self.assertMatch(result, letter_b)

    def test_search_more_like_this_by_attachment(self):
        letter_a = AttachmentFactory(attachment__text=self.text).letter
        letter_b = AttachmentFactory(attachment__text=self.text).letter
        self.index([letter_a, letter_b])

        doc = find_document(letter_a.pk)
        result = more_like_this(doc)

        self.assertMatch(result, letter_b)


class IndexCommandTestCase(ESMixin, TestCase):
    def test_single_letter_command(self):
        letter = IncomingLetterFactory()
        delete_document(letter.pk)
        call_command("es_index", "--skip-queue", stdout=StringIO())
        time.sleep(5)
        result = search_keywords(letter.title)

        self.assertMatch(result, letter)
