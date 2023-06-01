import factory.fuzzy

from feder.letters.factories import AttachmentFactory
from feder.virus_scan.models import Request


class AttachmentRequestFactory(factory.django.DjangoModelFactory):
    content_object = factory.SubFactory(AttachmentFactory)
    field_name = "attachment"

    class Meta:
        model = Request
