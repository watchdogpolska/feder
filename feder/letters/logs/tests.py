import hashlib
import inspect
import json
import os

from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_text
from vcr import VCR

from feder.cases.factories import CaseFactory
from feder.letters.factories import LetterFactory, SendOutgoingLetterFactory
from feder.letters.logs.factories import get_emaillabs_row, LogRecordFactory
from feder.letters.logs.models import LogRecord, EmailLog, STATUS
from feder.letters.logs.utils import get_emaillabs_client
from feder.main.tests import PermissionStatusMixin
from feder.users.factories import UserFactory

SEED = os.urandom(10)


def scrub_text(x, seed):
    """
    Anonymizes data by using salt and unidirectional hash function.
    Identical data in one cassette will be identical (comparable).

    :param x: string to anonymise
    :param seed: value modification parameter
    :return: anonymized text
    """
    return hashlib.sha1(force_text(x).encode("utf-8") + seed).hexdigest()


def generator(f):
    filename = "{}.PY3.{}".format(f.__self__.__class__.__name__, f.__name__)
    return os.path.join(os.path.dirname(inspect.getfile(f)), "cassettes", filename)


def scrub_response(seed, fields=None):
    fields = fields or ["to", "from", "subject", "account"]

    def before_record_response(response):
        data = json.loads(response["body"]["string"].decode("utf-8"))
        for i, row in enumerate(data["data"]):
            for field in fields:
                if field in row:
                    data["data"][i][field] = scrub_text(row[field], seed)
        response["body"]["string"] = json.dumps(data).encode("utf-8")
        return response

    return before_record_response


my_vcr = VCR(
    func_path_generator=generator,
    decode_compressed_response=True,
    serializer="yaml",
    filter_headers=["authorization"],
    before_record_response=scrub_response(SEED),
    path_transformer=VCR.ensure_suffix(".yaml"),
)


class EmailLabsClientTestCase(TestCase):
    @my_vcr.use_cassette()
    def test_get_emails(self):
        client = get_emaillabs_client(per_page=20)
        self.assertEqual(len(client.get_emails()), 20)

    @my_vcr.use_cassette()
    def test_get_emails_iter(self):
        client = get_emaillabs_client(per_page=20)
        data = list(client.get_emails_iter())
        self.assertTrue(len(data) > 20, msg="Found {} messages.".format(len(data)))


class LogRecordQuerySet(TestCase):
    def setUp(self):
        self.letter = LetterFactory()
        self.letter_no_case = LetterFactory(record__case=None)
        self.rows = [
            get_emaillabs_row(
                sender_from=self.letter.case.email, id="ID1", deferred_time="Now"
            ),
            get_emaillabs_row(sender_from="sprawa@example.com", id="ID1"),
            get_emaillabs_row(sender_from="sprawa2@example.com", id="ID2"),
        ]

    def test_parse_rows_counters(self):
        skipped, saved = LogRecord.objects.parse_rows(self.rows)
        self.assertEquals(saved, 1)
        self.assertEquals(skipped, 2)

    def test_parse_rows_create_email_log(self):
        LogRecord.objects.parse_rows(self.rows)
        self.assertEqual(EmailLog.objects.count(), 1)
        self.assertTrue(
            EmailLog.objects.filter(email_id="ID1", case=self.letter.case).exists()
        )

    def test_parse_rows_create_log_record(self):
        LogRecord.objects.parse_rows(self.rows)
        self.assertEqual(LogRecord.objects.count(), 1)
        self.assertTrue(
            LogRecord.objects.filter(
                email__case=self.letter.case, email__email_id="ID1"
            ).exists()
        )

    def test_parse_rows_update_status(self):
        LogRecord.objects.parse_rows(self.rows)
        self.assertEqual(EmailLog.objects.get().status, STATUS.deferred)
        LogRecord.objects.parse_rows(
            [
                get_emaillabs_row(
                    sender_from=self.letter.case.email, id="ID1", ok_time="Now"
                )
            ]
        )
        self.assertEqual(EmailLog.objects.get().status, STATUS.ok)
        self.assertEqual(LogRecord.objects.count(), 2)

    def test_parse_identify_message_by_id(self):
        letter = SendOutgoingLetterFactory()
        msg_id = letter.message_id_header
        row = get_emaillabs_row(sender_from=letter.case.email, message_id=msg_id)
        skipped, saved = LogRecord.objects.parse_rows([row])
        self.assertEqual(saved, 1)
        self.assertEqual(EmailLog.objects.get().letter, letter)


class ObjectMixin:
    def setUp(self):
        self.user = UserFactory(username="john")
        self.record = LogRecordFactory()
        self.emaillog = self.record.email
        self.case = self.emaillog.case
        self.monitoring = self.case.monitoring
        self.permission_object = self.monitoring


class EmailLogMonitoringListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_log"]

    def get_url(self):
        return reverse("logs:list", kwargs={"monitoring_pk": self.monitoring.pk})


class EmailLogMonitoringCsvViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_log"]

    def get_url(self):
        return reverse("logs:export", kwargs={"monitoring_pk": self.monitoring.pk})

    def test_has_logs(self):
        logrecord_for_another_monitoring = LogRecordFactory()
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTrue(
            response.get("Content-Disposition").startswith("attachment;filename=")
        )
        self.assertContains(response, self.emaillog.case.institution)
        self.assertNotContains(
            response,
            logrecord_for_another_monitoring.email.case.institution.name,
            200,
            (
                "Csv export for a monitoring should not "
                "contain emaillogs for another monitoring"
            ),
        )


class EmailLogCaseListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_log"]

    def get_url(self):
        return reverse("logs:list", kwargs={"case_pk": self.case.pk})

    def test_shows_self_case(self):
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertContains(response, self.case.name)

    def test_shows_only_own_case(self):
        self.login_permitted_user()
        extra_cases = CaseFactory.create_batch(monitoring=self.monitoring, size=25)
        response = self.client.get(self.get_url())
        for case in extra_cases:
            self.assertNotContains(response, case.name)


class EmailLogDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_log"]

    def get_url(self):
        return reverse("logs:detail", kwargs={"pk": self.emaillog.pk})


class LogRecordTestCase(TestCase):
    def test_get_status(self):
        data = {
            "ok_desc": "250 2.0.0 Ok: queued as A3B925BF18",
            "account": "1.siecobywatelska.smtp",
            "tracking": [],
            "from": "sprawa-3070@example.com",
            "open_time": None,
            "vps": "smtp2-87",
            "tags": [],
            "injected_time": "2017-08-24 17:25:50",
            "created_at": None,
            "updated_at": None,
            "message_id": "20170824152549.2577.77274@localhost",
            "to": "target@example.com",
            "postfix_id": ["3xdSmZ0kpMz6jsBt", "3xdSmZ2ZvWz6Q7V0"],
            "ok_time": "2017-08-24 17:25:50",
            "open_desc": None,
            "uid": "b1db7556ea65065c69d86b81ef248eb5",
            "id": "599ef08c42cf33b253fdc5f6",
            "subject": "Wniosek o udost\u0119pnienie informacji publicznej",
        }
        self.assertEqual(LogRecord(data=data).get_status(), "ok")
