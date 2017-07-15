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
        call_command('drop_duplicate_ids', '--no-progress', stdout=self.out, stderr=self.err)
        Letter.objects.get(pk=self.original_msg.pk)
        with self.assertRaises(Letter.DoesNotExist):
            Letter.objects.get(pk=self.duplicate_msg.pk)

    def test_dry_run_not_delete_message(self):
        call_command('drop_duplicate_ids', '--no-progress', '--dry-run', stdout=self.out, stderr=self.err)
        Letter.objects.get(pk=self.original_msg.pk)
        Letter.objects.get(pk=self.duplicate_msg.pk)

    def test_finish_message_stats(self):
        call_command('drop_duplicate_ids', '--no-progress', '--dry-run', stdout=self.out, stderr=self.err)
        self.assertIn('There is 1 cases containing 2 letters of which 1 were removed.', self.out.getvalue())
