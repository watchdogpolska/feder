import factory

from feder.institutions.factories import InstitutionFactory
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory

from .models import Alias, Case


class CaseFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("case-{}".format)
    user = factory.SubFactory(UserFactory)
    institution = factory.SubFactory(InstitutionFactory)
    email = factory.Sequence("case-email-{}@example.com".format)

    @factory.lazy_attribute
    def monitoring(self):
        return MonitoringFactory(user=self.user)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of tags were passed in, use them
            for tag in extracted:
                self.tags.add(tag)

    class Meta:
        model = Case


class AliasFactory(factory.django.DjangoModelFactory):
    case = factory.SubFactory(CaseFactory)
    email = factory.Sequence("alias-email-{}@example.com".format)

    class Meta:
        model = Alias
