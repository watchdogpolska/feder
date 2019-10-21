from django.test import TestCase

from feder.letters.factories import IncomingLetterFactory
from feder.letters.models import Letter
from feder.parcels.factories import IncomingParcelPostFactory, OutgoingParcelPostFactory
from feder.records.models import Record


class RecordQuerySetTestCase(TestCase):
    def test_for_milestone_returns_letters(self):
        qs = Record.objects.for_milestone()
        self.assertFalse(
            qs.filter(
                letters_letters=IncomingLetterFactory(is_spam=Letter.SPAM.spam)
            ).exists()
        )
        self.assertTrue(
            qs.filter(
                letters_letters=IncomingLetterFactory(is_spam=Letter.SPAM.non_spam)
            ).exists()
        )

    def test_for_milestone_returns_parcels(self):
        qs = Record.objects.for_milestone()
        self.assertTrue(
            qs.filter(parcels_incomingparcelposts=IncomingParcelPostFactory()).exists()
        )
        self.assertTrue(
            qs.filter(parcels_outgoingparcelposts=OutgoingParcelPostFactory()).exists()
        )

    def test_with_select_related_content(self):
        ilf = IncomingLetterFactory()
        ipp = IncomingParcelPostFactory()
        with self.assertNumQueries(num=1):
            objects = list(Record.objects.with_select_related_content().all())
            self.assertEquals(objects[0].content_object, ilf)
            self.assertEquals(objects[1].content_object, ipp)

    def test_with_prefetch_related_content(self):
        ilf = IncomingLetterFactory()
        ipp = IncomingParcelPostFactory()
        ipp2 = IncomingParcelPostFactory()
        ipp3 = IncomingParcelPostFactory()

        with self.assertNumQueries(num=4):
            objects = list(Record.objects.with_prefetch_related_content().all())
            self.assertEquals(objects[0].content_object, ilf)
            self.assertEquals(objects[1].content_object, ipp)
            self.assertEquals(objects[2].content_object, ipp2)
            self.assertEquals(objects[3].content_object, ipp3)


class RecordTestCase(TestCase):
    def test_content_template(self):
        letter = IncomingLetterFactory()
        self.assertEqual(
            letter.record.content_template, "letters/_letter_content_item.html"
        )
