import random
from email.mime.text import MIMEText
from email.utils import make_msgid, parseaddr

import factory.fuzzy
from factory.django import FileField

from feder.institutions.factories import InstitutionFactory
from feder.records.factories import RecordFactory
from feder.users.factories import UserFactory
from .models import Letter, Attachment
from os.path import join, dirname

WORD_LIST_FILE = join(dirname(__file__), "fixtures/words.txt")

with open(WORD_LIST_FILE, encoding="utf-8") as fp:
    words = [x.strip() for x in fp.readlines()]


def get_text(size=25):
    return " ".join(random.choices(words, k=size))


def get_email(subject=None, from_=None, to=None, msg_id=None):
    msg = MIMEText("Lorem ipsum")
    msg["Subject"] = subject or "Example message"
    msg["From"] = from_ or "sender@example.com"
    msg["Message-ID"] = msg_id or make_msgid(
        domain=parseaddr(msg["From"])[1].split("@")[1]
    )
    msg["To"] = to or "recipient@example.com"
    return msg


class MailField(FileField):
    DEFAULT_FILENAME = "data.eml"

    def _make_data(self, params):
        return params.get("data", get_email(**params).as_string().encode("utf-8"))


class FileTextField(FileField):
    DEFAULT_FILENAME = "content.txt"

    def _make_data(self, params):
        return params.get("text", get_text().encode("utf-8"))


class LetterFactory(factory.django.DjangoModelFactory):
    record = factory.SubFactory(RecordFactory)
    title = factory.Sequence("title-letter-{}".format)
    body = factory.fuzzy.FuzzyAttribute(get_text)
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
    attachment = FileTextField()

    class Meta:
        model = Attachment
