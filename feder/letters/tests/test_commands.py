from StringIO import StringIO
from django.core.management import call_command
from django.test import TestCase

from feder.cases.factories import CaseFactory
from feder.letters.models import Letter
from feder.letters.tests.base import MessageMixin


class DropDuplicateIdsTestCase(MessageMixin, TestCase):
    def setUp(self):
        super(DropDuplicateIdsTestCase, self).setUp()
        self.case = CaseFactory(email='porady@REDACTED')
        self.original_msg = self.load_letter('basic_message.eml')
        self.duplicate_msg = self.load_letter('basic_message.eml')
        self.out = StringIO()
        self.err = StringIO()

    def test_duplicate_message_was_deleted(self):
        call_command('drop_duplicate_ids', '--no-progress', '--delete', stdout=self.out, stderr=self.err)
        Letter.objects.get(pk=self.original_msg.pk)
        with self.assertRaises(Letter.DoesNotExist):
            Letter.objects.get(pk=self.duplicate_msg.pk)

    def test_dry_run_not_delete_message(self):
        call_command('drop_duplicate_ids', '--no-progress', stdout=self.out, stderr=self.err)
        Letter.objects.get(pk=self.original_msg.pk)
        Letter.objects.get(pk=self.duplicate_msg.pk)

    def test_finish_message_stats(self):
        call_command('drop_duplicate_ids', '--no-progress', '--delete', stdout=self.out, stderr=self.err)
        self.assertIn('There is 1 cases containing 2 letters of which 1 were removed.', self.out.getvalue())


class LoadEmlTestCase(MessageMixin, TestCase):
    def test_command_style(self):
        out = StringIO()
        case = CaseFactory(email='case-123@fedrowanie.siecobywatelska.pl')
        path = self._get_email_path('message-with-content.eml')
        call_command('load_eml', self.mailbox.pk, path, stdout=out)
        self.assertIn("Imported ", out.getvalue())
        self.assertEqual(case.record_set.count(), 1)
