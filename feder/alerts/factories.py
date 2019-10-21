import factory

from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from .models import Alert


class AlertFactory(factory.django.DjangoModelFactory):
    monitoring = factory.SubFactory(MonitoringFactory)
    reason = factory.Sequence("reason-{0}".format)
    author = factory.SubFactory(UserFactory)

    class Meta:
        model = Alert
