# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import email

from django.core import mail
from django.test import TestCase
from django.utils import six

from feder.cases.models import Case
from feder.institutions.factories import InstitutionFactory
from feder.letters.utils import normalize_msg_id
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from ..factories import (IncomingLetterFactory, LetterFactory,
                         OutgoingLetterFactory, SendOutgoingLetterFactory)
from ..models import Letter


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
        self.assertGreater(len(str(incoming)), 0)

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
        if six.PY3:
            message = email.message_from_string(
                outgoing.eml.file.read().decode('utf-8'))
        else:  # Deprecated Python 2.7 support
            message = email.message_from_file(outgoing.eml.file)
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

    def test_send_new_case_adds_footer_from_monitoring(self):
        user = UserFactory(username="jerry")
        footer_text = "some footer zażółć gęślą jaźń"

        monitoring = MonitoringFactory(email_footer=footer_text)
        institution = InstitutionFactory()
        Letter.send_new_case(
            user=user,
            monitoring=monitoring,
            institution=institution,
            text="Przeslac informacje szybko"
        )
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Letter.objects.count(), 1)
        self.assertIn(
            footer_text, mail.outbox[0].body,
            "Email for a new case should contain footer text from monitoring"
        )
