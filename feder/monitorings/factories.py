import factory

from feder.domains.factories import DomainFactory
from feder.users.factories import UserFactory

from .models import Monitoring


class MonitoringFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "monitoring-%04d" % n)
    user = factory.SubFactory(UserFactory)
    description = factory.Sequence(lambda n: "description no.%04d" % n)
    subject = factory.Sequence(lambda n: "subject no.%04d" % n)
    template = factory.Sequence(lambda n: "template no.%04d. reply to {{EMAIL}}" % n)
    domain = factory.SubFactory(DomainFactory)

    class Meta:
        model = Monitoring
        django_get_or_create = ("name",)
