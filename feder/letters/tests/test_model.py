from email import message_from_file
from os.path import dirname, join

from django.core import mail
from django.test import TestCase
from django_mailbox.models import Mailbox

from feder.cases.factories import CaseFactory
from feder.cases.models import Case
from feder.institutions.factories import InstitutionFactory
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from ..factories import (IncomingLetterFactory, LetterFactory,
                         OutgoingLetterFactory)
from ..models import Letter, MessageParser


class ModelTestCase(TestCase):
    def test_is_incoming(self):
        self.assertTrue(IncomingLetterFactory().is_incoming)
        self.assertFalse(OutgoingLetterFactory().is_incoming)

    def test_is_outgoing(self):
        self.assertTrue(OutgoingLetterFactory().is_outgoing)
        self.assertFalse(IncomingLetterFactory().is_outgoing)

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


class IncomingEmailTestCase(TestCase):
    def setUp(self):
        self.mailbox = Mailbox.objects.create(from_email='from@example.com')

    @staticmethod
    def _get_email_object(filename):  # See coddingtonbear/django-mailbox#89
        path = join(dirname(__file__), 'messages', filename)
        fp = open(path, 'rb')
        return message_from_file(fp)

    def get_message(self, filename):
        message = self._get_email_object(filename)
        msg = self.mailbox._process_message(message)
        msg.save()
        return msg

    def test_case_identification(self):
        case = CaseFactory(email='porady@REDACTED')
        message = self.get_message('basic_message.eml')
        letter = MessageParser(message).insert()
        self.assertEqual(letter.case, case)
        self.assertEqual(letter.attachment_set.count(), 2)
