from django.test import RequestFactory, TestCase

from feder.letters.factories import AttachmentFactory, IncomingLetterFactory
from feder.parcels.factories import IncomingParcelPostFactory, OutgoingParcelPostFactory
from feder.records.serializers import RecordSerializer


class RecordSerializerTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.context = {"request": self.request}

    def test_serialization_of_letter(self):
        attachment = AttachmentFactory(letter=IncomingLetterFactory())
        result = RecordSerializer(
            instance=attachment.letter.record, context=self.context
        ).data
        self.assertEqual(result["content_object"]["title"], attachment.letter.title)
        attachments = result["content_object"]["attachments"]
        self.assertEqual(len(attachments), 1)
        attachment = attachments[0]
        self.assertTrue(attachment["url"].startswith("http"))

    def test_serialization_of_incomingparcel(self):
        parcel = IncomingParcelPostFactory()
        result = RecordSerializer(instance=parcel.record, context=self.context).data
        self.assertEqual(result["content_object"]["title"], parcel.title)

    def test_serialization_of_outgoingparcel(self):
        parcel = OutgoingParcelPostFactory()
        result = RecordSerializer(instance=parcel.record, context=self.context).data
        self.assertEqual(result["content_object"]["title"], parcel.title)
