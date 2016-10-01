import factory
from feder.teryt.factories import JSTFactory

from .models import Institution, Tag


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('institution-{0}'.format)
    jst = factory.SubFactory(JSTFactory)
    email = factory.Sequence('email-{0}@example.com'.format)

    class Meta:
        model = Institution


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('tag-{0}'.format)

    class Meta:
        model = Tag
