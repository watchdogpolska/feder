import factory

from feder.cases.factories import CaseFactory
from feder.records.models import Record


class RecordFactory(factory.django.DjangoModelFactory):
    case = factory.SubFactory(CaseFactory)

    class Meta:
        model = Record
