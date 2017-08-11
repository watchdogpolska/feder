import factory
import factory.fuzzy

from feder.cases.factories import CaseFactory
from feder.institutions.factories import InstitutionFactory
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
    email = factory.Sequence('xxx-{0}@example.com'.format)
    note = factory.fuzzy.FuzzyText()


class OutgoingLetterFactory(LetterFactory):
    author_user = factory.SubFactory(UserFactory)
