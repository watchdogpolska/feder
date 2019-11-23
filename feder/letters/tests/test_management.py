from django.core.management import call_command
from feder.cases.factories import CaseFactory
from feder.letters.factories import IncomingLetterFactory, OutgoingLetterFactory
from django.test import TestCase
from feder.letters.models import Letter
from io import StringIO


class FixDuplicateMailTestCase(TestCase):
    def test_delete_only_duplicated(self):
        case = CaseFactory()
        in1 = IncomingLetterFactory(record__case=case)
        in2 = IncomingLetterFactory(record__case=case)
        ou1 = OutgoingLetterFactory(record__case=case)
        in_static_id = IncomingLetterFactory(
            record__case=case, eml__msg_id="xxxx@example.com"
        )
        in_dupe_id = IncomingLetterFactory(
            record__case=case, eml__msg_id="xxxx@example.com"
        )
        stdout = StringIO()
        call_command(
            "fix_duplicate_mail",
            "--monitoring-pk={}".format(case.monitoring.pk),
            "--delete",
            stdout=stdout,
        )
        self.assertTrue(Letter.objects.filter(pk=in1.id).exists())
        self.assertTrue(Letter.objects.filter(pk=in2.id).exists())
        self.assertTrue(Letter.objects.filter(pk=ou1.id).exists())
        self.assertTrue(Letter.objects.filter(pk=in_static_id.id).exists())
        self.assertFalse(Letter.objects.filter(pk=in_dupe_id.id).exists())

    def test_delete_only_when_force_delete(self):
        case = CaseFactory()
        IncomingLetterFactory(record__case=case, eml__msg_id="xxxx@example.com")
        in_dupe_id = IncomingLetterFactory(
            record__case=case, eml__msg_id="xxxx@example.com"
        )
        stdout = StringIO()
        call_command(
            "fix_duplicate_mail",
            "--monitoring-pk={}".format(case.monitoring.pk),
            stdout=stdout,
        )
        self.assertTrue(Letter.objects.filter(pk=in_dupe_id.id).exists())
        call_command(
            "fix_duplicate_mail",
            "--monitoring-pk={}".format(case.monitoring.pk),
            "--delete",
            stdout=stdout,
        )
        self.assertFalse(Letter.objects.filter(pk=in_dupe_id.id).exists())
