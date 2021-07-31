import factory

from .models import Organisation


class OrganisationFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("organisation-{}".format)

    class Meta:
        model = Organisation
