from feder.cases import models
from feder.institutions.factories import factory_institution
from feder.monitorings.factories import factory_monitoring
import factory
from feder.users.factory import UserFactory


class CaseFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'case-{0}'.format(n))
    user = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def monitoring(self):
        return factory_monitoring(self.user)

    @factory.lazy_attribute
    def institution(self):
        return factory_institution(self.user)

    class Meta:
        model = models.Case


def factory_case(user):
        return CaseFactory(user=user)
