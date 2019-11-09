import factory

from feder.teryt.factories import JSTFactory
from .models import Institution, Tag


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("institution-{}".format)
    jst = factory.SubFactory(JSTFactory)
    email = factory.Sequence("email-{}@example.com".format)

    class Meta:
        model = Institution


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("tag-{}".format)

    class Meta:
        model = Tag
