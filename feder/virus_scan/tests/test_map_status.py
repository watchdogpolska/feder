from unittest.mock import patch

from django.test import TestCase

from feder.virus_scan.engine.attachmentscanner import AttachmentScannerEngine
from feder.virus_scan.engine.metadefender import MetaDefenderEngine
from feder.virus_scan.engine.virustotal import VirusTotalEngine
from feder.virus_scan.models import Request


class VirusTotalReceiveResultTestCase(TestCase):
    def _receive(self, results):
        with patch.object(VirusTotalEngine, "__init__", lambda self: None):
            engine = VirusTotalEngine()
            engine.client = type(
                "FakeClient",
                (),
                {"get_file_report": lambda self, engine_id: {"results": results}},
            )()
            engine.delay = 0
            return engine.receive_result("some-id")

    def test_real_malware_is_infected(self):
        result = self._receive(
            {
                "response_code": 1,
                "total": 10,
                "positives": 1,
                "resource": "x",
                "permalink": "http://example.com",
                "scans": {
                    "Engine1": {"detected": True, "result": "Trojan.GenericKD"},
                    "Engine2": {"detected": False, "result": None},
                },
            }
        )
        self.assertEqual(result["status"], Request.STATUS.infected)

    def test_only_encryption_heuristic_is_password_protected(self):
        result = self._receive(
            {
                "response_code": 1,
                "total": 10,
                "positives": 1,
                "resource": "x",
                "permalink": "http://example.com",
                "scans": {
                    "ClamAV": {
                        "detected": True,
                        "result": "Heuristics.Encrypted.Zip",
                    },
                    "Engine2": {"detected": False, "result": None},
                },
            }
        )
        self.assertEqual(result["status"], Request.STATUS.password_protected)

    def test_mixed_encryption_and_malware_stays_infected(self):
        result = self._receive(
            {
                "response_code": 1,
                "total": 10,
                "positives": 2,
                "resource": "x",
                "permalink": "http://example.com",
                "scans": {
                    "ClamAV": {
                        "detected": True,
                        "result": "Heuristics.Encrypted.Zip",
                    },
                    "Engine2": {"detected": True, "result": "Trojan.GenericKD"},
                },
            }
        )
        self.assertEqual(result["status"], Request.STATUS.infected)

    def test_clean_is_not_detected(self):
        result = self._receive(
            {
                "response_code": 1,
                "total": 10,
                "positives": 0,
                "resource": "x",
                "permalink": "http://example.com",
            }
        )
        self.assertEqual(result["status"], Request.STATUS.not_detected)


class MetaDefenderMapStatusTestCase(TestCase):
    def setUp(self):
        with patch.object(MetaDefenderEngine, "get_api_key", lambda self: None):
            self.engine = MetaDefenderEngine()

    def test_real_malware_is_infected(self):
        status = self.engine.map_status(
            {
                "status": "done",
                "process_info": {"progress_percentage": 100},
                "scan_results": {
                    "scan_all_result_i": 1,
                    "scan_all_result_a": "Infected",
                    "scan_details": {
                        "Engine1": {"threat_found": "Trojan.GenericKD"},
                    },
                },
            }
        )
        self.assertEqual(status, Request.STATUS.infected)

    def test_password_protected_aggregate_result_is_password_protected(self):
        status = self.engine.map_status(
            {
                "status": "done",
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Blocked",
                    "blocked_reason": "Password Protected Document",
                    "verdicts": ["No Threat Detected", "Password Protected Document"],
                },
                "scan_results": {
                    "scan_all_result_i": 15,
                    "scan_all_result_a": "Password Protected Document",
                    # Real-world MetaDefender responses leave threat_found
                    # empty per-engine even when scan_result_i > 0; the
                    # reason only appears in the aggregate fields above.
                    "scan_details": {
                        "ESET": {"threat_found": "", "scan_result_i": 10},
                        "Bitdefender": {"threat_found": "", "scan_result_i": 10},
                    },
                },
            }
        )
        self.assertEqual(status, Request.STATUS.password_protected)

    def test_clean_is_not_detected(self):
        status = self.engine.map_status(
            {
                "status": "done",
                "process_info": {"progress_percentage": 100},
                "scan_results": {
                    "scan_all_result_i": 0,
                    "scan_all_result_a": "No Threat Detected",
                },
            }
        )
        self.assertEqual(status, Request.STATUS.not_detected)

    def test_blocked_with_actual_av_detection_is_infected(self):
        status = self.engine.map_status(
            {
                "status": "done",
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Blocked",
                    "blocked_reason": "Infected",
                },
                "scan_results": {
                    "scan_all_result_a": "Infected",
                    "scan_all_result_i": 1,
                    "total_detected_avs": 2,
                },
            }
        )
        self.assertEqual(status, Request.STATUS.infected)

    def test_blocked_for_unrelated_policy_reason_is_suspicious(self):
        status = self.engine.map_status(
            {
                "status": "done",
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Blocked",
                    "blocked_reason": "File Type Restriction",
                },
                "scan_results": {
                    "scan_all_result_a": "File Type Restriction",
                    "scan_all_result_i": 1,
                    "total_detected_avs": 0,
                },
            }
        )
        self.assertEqual(status, Request.STATUS.suspicious)

    def test_allowed_with_nonzero_aggregate_code_is_not_detected(self):
        # Real-world MetaDefender Cloud response: a separate AI-generated
        # -content add-on feature sets a nonzero scan_all_result_i even
        # though zero AV engines detected anything and MetaDefender's own
        # policy engine allowed the file through.
        status = self.engine.map_status(
            {
                "status": "done",
                "process_info": {
                    "progress_percentage": 100,
                    "result": "Allowed",
                    "verdicts": ["AI Generated", "No Threat Detected"],
                    "blocked_reason": "",
                },
                "scan_results": {
                    "scan_all_result_a": "AI Generated",
                    "scan_all_result_i": 63,
                    "total_detected_avs": 0,
                    "current_av_result_a": "No Threat Detected",
                    "current_av_result_i": 0,
                },
            }
        )
        self.assertEqual(status, Request.STATUS.not_detected)


class AttachmentScannerMapStatusTestCase(TestCase):
    def setUp(self):
        self.engine = AttachmentScannerEngine()

    def test_found_is_infected(self):
        self.assertEqual(self.engine.map_status("found"), Request.STATUS.infected)

    def test_warning_is_suspicious_not_infected(self):
        self.assertEqual(self.engine.map_status("warning"), Request.STATUS.suspicious)

    def test_ok_is_not_detected(self):
        self.assertEqual(self.engine.map_status("ok"), Request.STATUS.not_detected)
