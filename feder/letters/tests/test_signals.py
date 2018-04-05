from __future__ import unicode_literals
from django.test import TestCase

from feder.alerts.models import Alert
from feder.cases.factories import CaseFactory
from feder.letters.factories import get_email
from feder.letters.signals import MessageParser
from feder.letters.tests.base import MessageMixin


class MessageParserTestCase(MessageMixin, TestCase):
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
        CaseFactory(email='case-123@fedrowanie.siecobywatelska.pl')
        message = self.get_message('message-with-content.eml')
        letter = MessageParser(message).insert()
        letter.refresh_from_db()
        # TODO: Debug changes Travis & local result
        self.assertIn(letter.title, ["Przeczytano: Wniosek o udost\u0119pnienie informacji publicznej",
                                     "Przeczytano: Wniosek o udost?pnienie informacji publicznej"])
        self.assertIn('odczytano w dniu ', letter.body)
        self.assertEqual(letter.quote, '')

    def test_report_detected_spam(self):
        case = CaseFactory()
        msg = get_email(to=case.email)
        msg['X-Spam-Flag'] = 'YES'
        MessageParser(self.mailbox._process_message(msg)).insert()
        self.assertEqual(Alert.objects.count(), 1)

    def test_report_only_detected_spam(self):
        case = CaseFactory()
        msg = get_email(to=case.email)
        msg['X-Spam-Flag'] = 'NO'
        MessageParser(self.mailbox._process_message(msg)).insert()
        self.assertEqual(Alert.objects.count(), 1)
