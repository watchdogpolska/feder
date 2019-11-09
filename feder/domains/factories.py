import factory

from .models import Domain


class DomainFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("case-{}.com".format)

    class Meta:
        model = Domain
