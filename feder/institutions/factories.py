import factory
from feder.teryt.factories import JSTFactory

from .models import Institution, Email, Tag


class EmailFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence('email-{0}'.format)
    institution = factory.SubFactory('feder.institutions.factories.InstitutionFactory')

    class Meta:
        model = Email


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('institution-{0}'.format)
    jst = factory.SubFactory(JSTFactory)

    class Meta:
        model = Institution


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('tag-{0}'.format)

    class Meta:
        model = Tag
