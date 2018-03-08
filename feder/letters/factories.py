from email.mime.text import MIMEText

import factory
import factory.fuzzy
from django.core.mail import EmailMessage
from factory.django import FileField

from feder.cases.factories import CaseFactory
from feder.institutions.factories import InstitutionFactory
from feder.users.factories import UserFactory
from .models import Letter


class MailField(FileField):
    DEFAULT_FILENAME = 'data.eml'

    def _make_data(self, params):
        msg = MIMEText("Lorem ipsum")
        msg['Subject'] = "Example message"
        msg['From'] = "sender@example.com"
        msg['To'] = "recipient@example.com"

        return params.get('data', msg.as_string().encode('utf-8'))


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
    eml = MailField()


class OutgoingLetterFactory(LetterFactory):
    author_user = factory.SubFactory(UserFactory)
    is_draft = False
    eml = MailField()


class DraftLetterFactory(OutgoingLetterFactory):
    is_draft = True


class SendOutgoingLetterFactory(LetterFactory):
    author_user = factory.SubFactory(UserFactory)

    is_send_yes = factory.PostGenerationMethodCall('send')
