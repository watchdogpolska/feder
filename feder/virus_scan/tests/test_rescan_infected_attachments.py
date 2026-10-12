from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from feder.virus_scan.engine.virustotal import VirusTotalEngine
from feder.virus_scan.factories import AttachmentRequestFactory
from feder.virus_scan.models import Request


class RescanInfectedAttachmentsTestCase(TestCase):
    def test_reclassifies_metadefender_password_protected(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="MetaDefender",
            engine_report={
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Blocked",
                    "blocked_reason": "Password Protected Document",
                },
                "scan_results": {
                    "scan_all_result_a": "Password Protected Document",
                    "scan_all_result_i": 15,
                    "total_detected_avs": 0,
                },
            },
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.password_protected)

    def test_reclassifies_metadefender_allowed_ai_generated(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="MetaDefender",
            engine_report={
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Allowed",
                    "blocked_reason": "",
                },
                "scan_results": {
                    "scan_all_result_a": "AI Generated",
                    "scan_all_result_i": 63,
                    "total_detected_avs": 0,
                },
            },
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.not_detected)

    def test_real_malware_is_left_infected(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="MetaDefender",
            engine_report={
                "process_info": {"progress_percentage": 100, "result": "Blocked"},
                "scan_results": {
                    "scan_all_result_a": "Infected",
                    "scan_all_result_i": 1,
                    "total_detected_avs": 2,
                },
            },
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.infected)

    def test_dry_run_does_not_save(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="MetaDefender",
            engine_report={
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Allowed",
                },
                "scan_results": {
                    "scan_all_result_a": "AI Generated",
                    "scan_all_result_i": 63,
                    "total_detected_avs": 0,
                },
            },
        )

        call_command("rescan_infected_attachments", "--dry-run", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.infected)

    def test_unknown_engine_is_skipped_without_error(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="SomeFutureEngine",
            engine_report={"anything": "goes"},
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.infected)

    def test_other_statuses_untouched_by_default(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.suspicious,
            engine_name="MetaDefender",
            engine_report={
                "process_info": {"progress_percentage": 100, "result": "Allowed"},
                "scan_results": {
                    "scan_all_result_a": "AI Generated",
                    "scan_all_result_i": 63,
                    "total_detected_avs": 0,
                },
            },
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.suspicious)

    def test_status_option_targets_other_status(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.suspicious,
            engine_name="MetaDefender",
            engine_report={
                "process_info": {"progress_percentage": 100, "result": "Allowed"},
                "scan_results": {
                    "scan_all_result_a": "AI Generated",
                    "scan_all_result_i": 63,
                    "total_detected_avs": 0,
                },
            },
        )

        call_command(
            "rescan_infected_attachments",
            "--status",
            "suspicious",
            stdout=StringIO(),
        )

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.not_detected)

    def test_reclassifies_virustotal_report(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="VirusTotal",
            engine_report={
                "positives": 1,
                "scans": {
                    "ClamAV": {
                        "detected": True,
                        "result": "Heuristics.Encrypted.Zip",
                    },
                },
            },
        )

        # VirusTotalEngine's constructor wraps a third-party client that
        # raises if no API key is configured, which is the case in this
        # dev/test environment (only MetaDefender is set up) - bypass it to
        # test the classification logic in isolation.
        with patch.object(VirusTotalEngine, "__init__", lambda self: None):
            call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.password_protected)

    def test_unconfigured_engine_is_skipped_without_error(self):
        # Without the patch above, constructing VirusTotalEngine raises in
        # this environment - the command must catch that and skip, not crash.
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="VirusTotal",
            engine_report={"positives": 1, "scans": {}},
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.infected)

    def test_reclassifies_attachmentscanner_report(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="Attachmentscanner",
            engine_report={"status": "warning"},
        )

        call_command("rescan_infected_attachments", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.suspicious)


class ResubmitInfectedAttachmentsTestCase(TestCase):
    def test_resubmit_resets_matching_status_to_created(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="MetaDefender",
            engine_report={"scan_results": {"scan_all_result_i": 1}},
        )

        call_command("rescan_infected_attachments", "--resubmit", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.created)

    def test_resubmit_dry_run_does_not_save(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.infected,
            engine_name="MetaDefender",
            engine_report={"scan_results": {"scan_all_result_i": 1}},
        )

        call_command(
            "rescan_infected_attachments",
            "--resubmit",
            "--dry-run",
            stdout=StringIO(),
        )

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.infected)

    def test_resubmit_leaves_other_statuses_untouched(self):
        request = AttachmentRequestFactory(
            status=Request.STATUS.suspicious,
            engine_name="MetaDefender",
            engine_report={"scan_results": {"scan_all_result_i": 1}},
        )

        call_command("rescan_infected_attachments", "--resubmit", stdout=StringIO())

        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.suspicious)
