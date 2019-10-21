import factory

from feder.institutions.factories import InstitutionFactory
from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost
from feder.records.factories import RecordFactory
from feder.users.factories import UserFactory


class AbstractParcelPostFactory(factory.django.DjangoModelFactory):
    record = factory.SubFactory(RecordFactory)
    title = factory.Sequence("title-{0}".format)
    content = factory.django.ImageField()
    created_by = factory.SubFactory(UserFactory)


class IncomingParcelPostFactory(AbstractParcelPostFactory):
    sender = factory.SubFactory(InstitutionFactory)
    comment = factory.Sequence("comment-{0}".format)

    class Meta:
        model = IncomingParcelPost


class OutgoingParcelPostFactory(AbstractParcelPostFactory):
    recipient = factory.SubFactory(InstitutionFactory)

    class Meta:
        model = OutgoingParcelPost
