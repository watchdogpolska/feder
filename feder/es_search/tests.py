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
from pprint import pprint


class ESMixin:
    connection_alias = "default"
    index_delay = 1
    _index_suffix = "_test"
    documents = [LetterDocument]

    def setUp(self):
        super().setUp()
        for document in self.documents:
            document._index._orig_name = f"{document._index._name}"
            document._index._name += self._index_suffix
            document._index.delete(ignore=[404, 400])
            document._index.create(ignore=[404, 400])

    def tearDown(self):
        for document in self.documents:
            document._index.delete(ignore=[404, 400])
            document._index._name = document._index._orig_name

    def refresh_all(self):
        es = get_connection()
        for document in self.documents:
            index = document._index
            index.flush()
            index.refresh()
            # index.clear_cache()
            # index.forcemerge()
            # pprint(index.stats())
        # pprint(es.cluster.health(wait_for_status='yellow'))
        time.sleep(self.index_delay)

    def assertMatch(self, result, items):
        items = items if isinstance(items, Iterable) else [items]
        self.assertEqual(len(result), len(items))
        for obj in items:
            self.assertTrue(any(x.title == obj.title for x in result))

    def index(self, items):
        items = items if isinstance(items, Iterable) else [items]
        pks = [x.pk for x in items]
        index_letter.now(pks)
        self.refresh_all()
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
        letter_b = AttachmentFactory(
            attachment__text=self.text,
            # letter__title=letter_a.title,
            # letter__body=letter_a.body
        ).letter
        self.index([letter_a, letter_b])

        doc = find_document(letter_a.pk)
        print(doc)
        result = more_like_this(doc)
        print(result)

        self.assertMatch(result, letter_b)


class IndexCommandTestCase(ESMixin, TestCase):
    def test_single_letter_command(self):
        letter = IncomingLetterFactory()
        delete_document(letter.pk)
        call_command("es_index", "--skip-queue", stdout=StringIO())
        time.sleep(5)
        result = search_keywords(letter.title)

        self.assertMatch(result, letter)
