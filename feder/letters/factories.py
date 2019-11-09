from email.mime.text import MIMEText

import factory.fuzzy
from factory.django import FileField

from feder.institutions.factories import InstitutionFactory
from feder.records.factories import RecordFactory
from feder.users.factories import UserFactory
from .models import Letter, Attachment


def get_email(subject=None, from_=None, to=None):
    msg = MIMEText("Lorem ipsum")
    msg["Subject"] = subject or "Example message"
    msg["From"] = from_ or "sender@example.com"
    msg["To"] = to or "recipient@example.com"
    return msg


class MailField(FileField):
    DEFAULT_FILENAME = "data.eml"

    def _make_data(self, params):
        return params.get("data", get_email().as_string().encode("utf-8"))


class LetterFactory(factory.django.DjangoModelFactory):
    record = factory.SubFactory(RecordFactory)
    title = factory.Sequence("title-letter-{}".format)
    body = factory.Sequence("body-{}".format)
    quote = factory.Sequence("quote-{}".format)

    class Meta:
        model = Letter


class IncomingLetterFactory(LetterFactory):
    author_institution = factory.SubFactory(InstitutionFactory)
    email = factory.Sequence("xxx-{}@example.com".format)
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
    is_send_yes = factory.PostGenerationMethodCall("send")


class AttachmentFactory(factory.django.DjangoModelFactory):
    letter = factory.SubFactory(LetterFactory)
    attachment = factory.django.FileField()

    class Meta:
        model = Attachment
