import factory

from feder.monitorings.factories import MonitoringFactory
from .models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    monitoring = factory.SubFactory(MonitoringFactory)
    name = factory.Sequence("tag-{}".format)

    class Meta:
        model = Tag


class GlobalTagFactory(TagFactory):
    name = factory.Sequence("global-tag-{}".format)
    monitoring = None
