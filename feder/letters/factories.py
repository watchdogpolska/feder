import factory

from feder.cases.factories import CaseFactory
from feder.institutions.factories import InstitutionFactory, EmailFactory
from feder.users.factories import UserFactory

from .models import Letter


class LetterFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence('title-letter-{0}'.format)
    case = factory.SubFactory(CaseFactory)
    body = factory.Sequence('body-{0}'.format)
    quote = factory.Sequence('quote-{0}'.format)

    class Meta:
        model = Letter


class IncomingLetterFactory(LetterFactory):
    author_institution = factory.SubFactory(InstitutionFactory)
    email = factory.Sequence('xxx-{0}'.format)

    @factory.post_generation
    def email_obj(self, create, extracted, **kwargs):
        if not create:
            return
        EmailFactory(institution=self.case.institution,
                     email=self.email)


class OutgoingLetterFactory(LetterFactory):
    author_user = factory.SubFactory(UserFactory)
