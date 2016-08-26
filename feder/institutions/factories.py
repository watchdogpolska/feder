import factory
from feder.teryt.factories import JSTFactory

from .models import Institution


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('institution-{0}'.format)
    address = factory.Sequence('institution-{0}@example.com'.format)
    jst = factory.SubFactory(JSTFactory)

    class Meta:
        model = Institution
