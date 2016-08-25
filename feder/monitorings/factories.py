from .models import Monitoring
from feder.users.factories import UserFactory
import factory


class MonitoringFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'monitoring-%04d' % n)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Monitoring
        django_get_or_create = ('name', )
