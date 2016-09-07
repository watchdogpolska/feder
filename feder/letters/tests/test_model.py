from django.core import mail
from django.test import TestCase

from feder.cases.models import Case
from feder.institutions.factories import EmailFactory, InstitutionFactory
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory

from ..models import Letter
from ..factories import IncomingLetterFactory, OutgoingLetterFactory, LetterFactory


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
        email = EmailFactory(priority=25, institution=outgoing.case.institution)
        outgoing.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(email.email, mail.outbox[0].to)
        self.assertEqual(outgoing.email, email.email)

    def test_send_new_case(self):
        user = UserFactory(username="tom")
        email = EmailFactory()
        Letter.send_new_case(user=user,
                             monitoring=MonitoringFactory(),
                             institution=email.institution,
                             text="Przeslac informacje szybko")
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Letter.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(email.email, mail.outbox[0].to)
