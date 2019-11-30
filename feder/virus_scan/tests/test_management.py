from django.test import TestCase
from io import StringIO
from django.core.management import call_command
from io import StringIO
from feder.virus_scan.engine import get_engine
from feder.virus_scan.models import Request
from feder.virus_scan.factories import AttachmentRequestFactory
import time
import struct
import random

current_engine = get_engine()

EICAR_TEST = r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def random_binary():
    return struct.pack("=I", random.randint(0, ((2 ** 32) - 1)))


class VirusScanCommandTestCase(TestCase):
    def test_virus_scan_for_eicar(self):
        request = AttachmentRequestFactory(content_object__attachment__data=EICAR_TEST)
        stdout = StringIO()
        call_command(
            "virus_scan", stdout=stdout,
        )
        request.refresh_from_db()
        if request.status == Request.STATUS.queued:
            self._receive_until_transition(request)
        self.assertEqual(request.status, Request.STATUS.infected)
        self.assertEqual(request.engine_name, current_engine.name)
        self.assertNotEqual(request.engine_id, "")

    def test_virus_scan_for_safe_file(self):
        request = AttachmentRequestFactory()
        stdout = StringIO()
        call_command(
            "virus_scan", stdout=stdout,
        )
        request.refresh_from_db()
        if request.status == Request.STATUS.queued:
            self._receive_until_transition(request)
        self.assertEqual(request.status, Request.STATUS.not_detected)
        self.assertEqual(request.engine_name, current_engine.name)
        self.assertNotEqual(request.engine_id, "")

    def _receive_until_transition(self, obj, delay=10, timeout=180):
        initial_state = obj.status
        stdout = StringIO()

        for _ in range(round(timeout / delay)):
            call_command(
                "virus_scan", "--skip-send", stdout=stdout,
            )
            obj.refresh_from_db()
            if obj.status != initial_state:
                return
            # print("Waiting to transition state: {}".format(obj))
            time.sleep(delay)
        raise Exception("Timeout for transition of state")

    def test_virus_scan_file_for_random(self):
        request = AttachmentRequestFactory(
            content_object__attachment__data=random_binary()
        )
        stdout = StringIO()
        call_command(
            "virus_scan", "--skip-receive", stdout=stdout,
        )
        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.queued)
        self._receive_until_transition(request)
        self.assertEqual(request.status, Request.STATUS.not_detected)
