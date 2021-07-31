import factory
from ..organisations.factories import OrganisationFactory
from .models import Domain


class DomainFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("case-{}.com".format)
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = Domain
