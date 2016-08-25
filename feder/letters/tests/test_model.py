from django.core import mail
from django.test import TestCase

from feder.cases.factories import factory_case
from feder.cases.models import Case
from feder.institutions.factories import factory_institution
from feder.monitorings.factories import MonitoringFactory

from ..models import Letter

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="rob")
        self.l_u = Letter.objects.create(author_user=self.user,
                                         case=factory_case(self.user),
                                         title="Wniosek",
                                         body="Prosze przeslac informacje",
                                         email="X@wykop.pl")

        self.l_i = Letter.objects.create(author_institution=factory_institution(self.user),
                                         case=factory_case(self.user),
                                         title="Odpowiedz",
                                         body="W zalaczeniu.",
                                         email="karyna@gmina.pl")

    def test_is_incoming(self):
        self.assertTrue(self.l_i.is_incoming)
        self.assertFalse(self.l_u.is_incoming)

    def test_is_outgoing(self):
        self.assertTrue(self.l_u.is_outgoing)
        self.assertFalse(self.l_i.is_outgoing)

    def test_author(self):
        self.assertEqual(self.l_u.author, self.l_u.author_user)
        self.assertEqual(self.l_i.author, self.l_i.author_institution)

    def test_author_setter(self):
        u = User.objects.create(username="smith")
        self.l_u.author = u
        self.assertEqual(self.l_u.author_user, u)

        i = factory_institution(u)
        self.l_i.author = i
        self.assertEqual(self.l_i.author_institution, i)

        with self.assertRaises(ValueError):
            self.l_i.author = self.l_i

    def test_queryset_is_incoming(self):
        self.assertEqual(Letter.objects.is_outgoing().get(), self.l_u)

    def test_queryset_is_outgoing(self):
        self.assertEqual(Letter.objects.is_incoming().get(), self.l_i)

    def test_send(self):
        self.l_u.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.l_u.email, mail.outbox[0].to)

    def test_attachment_count(self):
        self.assertFalse(hasattr(Letter.objects.all()[0], 'attachment_count'))


class NewLetterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tom")

    def test_send_new(self):
        Letter.send_new_case(user=self.user,
                             monitoring=MonitoringFactory(user=self.user),
                             institution=factory_institution(self.user),
                             text="Przeslac informacje szybko")
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Letter.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
