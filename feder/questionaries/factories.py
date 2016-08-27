import factory

from feder.monitorings.factories import MonitoringFactory

from .models import Questionary


class QuestionaryFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence('questionary-{0}'.format)

    @factory.lazy_attribute
    def monitoring(self):
        return MonitoringFactory()

    class Meta:
        model = Questionary
