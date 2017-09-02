from __future__ import unicode_literals

from email import message_from_file

from django.core import mail
from django.test import TestCase

from feder.cases.factories import CaseFactory
from feder.cases.models import Case
from feder.institutions.factories import InstitutionFactory
from feder.letters.tests.base import MessageMixin
from feder.letters.utils import normalize_msg_id
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from ..factories import (IncomingLetterFactory, LetterFactory,
                         OutgoingLetterFactory, SendOutgoingLetterFactory)
from ..models import Letter, MessageParser
from django.conf import settings


class ModelTestCase(TestCase):
    def test_is_incoming(self):
        self.assertTrue(IncomingLetterFactory().is_incoming)
        self.assertFalse(OutgoingLetterFactory().is_incoming)

    def test_is_outgoing(self):
        self.assertTrue(OutgoingLetterFactory().is_outgoing)
        self.assertFalse(IncomingLetterFactory().is_outgoing)

    def test_default_subject(self):
        incoming = IncomingLetterFactory()
        incoming.title = ''
        self.assertEqual(settings.DEFAULT_LETTER_SUBJECT, str(incoming))

    def test_author_for_user(self):
        obj = OutgoingLetterFactory()
        self.assertEqual(obj.author, obj.author_user)

    def test_author_for_institution(self):
        obj = IncomingLetterFactory()
        self.assertEqual(obj.author, obj.author_institution)

    def test_author_setter_for_user(self):
        obj = LetterFactory()
        user = UserFactory(username="smith")
        obj.author = user
        self.assertEqual(obj.author_user, user)

    def test_authr_setter_for_institution(self):
        obj = LetterFactory()
        institution = InstitutionFactory()
        obj.author = institution
        self.assertEqual(obj.author_institution, institution)

    def test_author_setter_for_failable(self):
        with self.assertRaises(ValueError):
            LetterFactory().author = MonitoringFactory()

    def test_queryset_is_incoming(self):
        self.assertTrue(Letter.objects.is_incoming().
                        filter(pk=IncomingLetterFactory().pk).exists())
        self.assertFalse(Letter.objects.is_incoming().
                         filter(pk=OutgoingLetterFactory().pk).exists())

    def test_queryset_is_outgoing(self):
        self.assertFalse(Letter.objects.is_outgoing().
                         filter(pk=IncomingLetterFactory().pk).exists())
        self.assertTrue(Letter.objects.is_outgoing().
                        filter(pk=OutgoingLetterFactory().pk).exists())

    def test_send(self):
        outgoing = OutgoingLetterFactory()
        outgoing.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(outgoing.email, outgoing.case.institution.email)

        self.assertIn(outgoing.case.institution.email, mail.outbox[0].to)
        self.assertIn(outgoing.body, mail.outbox[0].body)
        self.assertIn(outgoing.quote, mail.outbox[0].body)

    def test_send_message_has_valid_msg_id(self):
        outgoing = SendOutgoingLetterFactory()

        self.assertTrue(outgoing.message_id_header)
        message = message_from_file(outgoing.eml.file)
        msg_id = normalize_msg_id(message['Message-ID'])
        self.assertEqual(outgoing.message_id_header, msg_id)

    def test_send_new_case(self):
        user = UserFactory(username="tom")
        institution = InstitutionFactory()
        Letter.send_new_case(user=user,
                             monitoring=MonitoringFactory(),
                             institution=institution,
                             text="Przeslac informacje szybko")
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Letter.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(institution.email, mail.outbox[0].to)


class IncomingEmailTestCase(MessageMixin, TestCase):
    def test_case_identification(self):
        case = CaseFactory(email='porady@REDACTED')
        message = self.get_message('basic_message.eml')
        letter = MessageParser(message).insert()
        self.assertEqual(letter.case, case)
        self.assertEqual(letter.attachment_set.count(), 2)

    def test_case_text_identification(self):
        CaseFactory(email='porady@REDACTED')
        message = self.get_message('basic_message.eml')
        letter = MessageParser(message).insert()
        self.assertEqual(letter.title, 'Odpowied\u017a od burmistrza na wniosek stowarzyszenia')
        self.assertEqual(letter.body, 'REDACTED')
        self.assertEqual(letter.quote, '')

    def test_case_text_identification_validation(self):
        """
        Validate regression of #280
        """
        CaseFactory(email='sprawa-REDACTED@fedrowanie.siecobywatelska.pl')
        message = self.get_message('message-with-content.eml')
        letter = MessageParser(message).insert()
        letter.refresh_from_db()
        # TODO: Debug changes Travis & local result
        self.assertIn(letter.title, ["Przeczytano: Wniosek o udost\u0119pnienie informacji publicznej",
                                     "Przeczytano: Wniosek o udost?pnienie informacji publicznej"])
        self.assertIn('odczytano w dniu ', letter.body)
        self.assertEqual(letter.quote, '')
