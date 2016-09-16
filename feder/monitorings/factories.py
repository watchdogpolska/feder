from .models import Monitoring
from feder.users.factories import UserFactory
import factory


class MonitoringFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'monitoring-%04d' % n)
    user = factory.SubFactory(UserFactory)
    description = factory.Sequence(lambda n: 'description no.%04d' % n)
    template = factory.Sequence(lambda n:
                                'template no.%04d. reply to {{EMAIL}}' % n)

    class Meta:
        model = Monitoring
        django_get_or_create = ('name', )
