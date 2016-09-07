import factory
from feder.teryt.factories import JSTFactory

from .models import Institution, Email


class EmailFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence('email-{0}'.format)
    institution = factory.SubFactory('feder.institutions.factories.InstitutionFactory')

    class Meta:
        model = Email


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('institution-{0}'.format)
    jst = factory.SubFactory(JSTFactory)

    email = factory.RelatedFactory(EmailFactory, 'institution')

    class Meta:
        model = Institution
