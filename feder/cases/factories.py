import factory

from feder.institutions.factories import InstitutionFactory
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from .models import Case, Alias


class CaseFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('case-{0}'.format)
    user = factory.SubFactory(UserFactory)
    institution = factory.SubFactory(InstitutionFactory)

    @factory.lazy_attribute
    def monitoring(self):
        return MonitoringFactory(user=self.user)

    class Meta:
        model = Case


class AliasFactory(factory.django.DjangoModelFactory):
    case = factory.SubFactory(CaseFactory)
    email = factory.Sequence('alias-email-{0}@example.com'.format)

    class Meta:
        model = Alias
