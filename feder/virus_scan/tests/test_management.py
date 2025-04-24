import os
import random
import struct
import time
from io import StringIO
from unittest import skipIf

from django.core.management import call_command
from django.test import TestCase

from feder.letters.factories import AttachmentFactory
from feder.virus_scan.engine import get_engine, is_available
from feder.virus_scan.factories import AttachmentRequestFactory
from feder.virus_scan.models import Request

EICAR_TEST = r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def random_binary():
    return struct.pack("=I", random.randint(0, ((2**32) - 1)))


def skipIfNoEngine(x):
    return skipIf(
        not is_available() and "CI" not in os.environ, "Missing engine configuration"
    )(x)


class VirusScanCommandTestCase(TestCase):
    @skipIfNoEngine
    def test_virus_scan_for_eicar(self):
        current_engine = get_engine()

        # Write the EICAR test string to a temporary file
        with open("/code/feder/media_prod/eicar_test.txt", "w") as f:
            f.write(EICAR_TEST)

        # Create an attachment object for the file
        attachment = AttachmentFactory(attachment="eicar_test.txt")

        # Create a request for the attachment
        request = AttachmentRequestFactory(content_object=attachment)
        stdout = StringIO()
        call_command(
            "virus_scan",
            "--skip-receive",
            "--skip-generate",
            stdout=stdout,
        )
        request.refresh_from_db()
        if request.status == Request.STATUS.queued:
            self._receive_until_transition(request)
        self.assertEqual(request.status, Request.STATUS.infected)
        self.assertEqual(request.engine_name, current_engine.name)
        self.assertNotEqual(request.engine_id, "")
        # Clean up the temporary file
        os.remove("/code/feder/media_prod/eicar_test.txt")

    @skipIfNoEngine
    def test_virus_scan_for_safe_file(self):
        current_engine = get_engine()

        request = AttachmentRequestFactory(content_object__attachment__data="zółć.docx")
        stdout = StringIO()
        call_command(
            "virus_scan",
            stdout=stdout,
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
                "virus_scan",
                "--skip-send",
                "--skip-generate",
                stdout=stdout,
            )
            obj.refresh_from_db()
            if obj.status != initial_state:
                return
            # print("Waiting to transition state: {}".format(obj))
            time.sleep(delay)
        raise Exception("Timeout for transition of state")

    @skipIfNoEngine
    def test_virus_scan_file_for_random(self):
        request = AttachmentRequestFactory(
            content_object__attachment__data=random_binary()
        )
        stdout = StringIO()
        call_command(
            "virus_scan",
            "--skip-receive",
            stdout=stdout,
        )
        request.refresh_from_db()
        self.assertEqual(request.status, Request.STATUS.queued)
        self._receive_until_transition(request)
        self.assertEqual(request.status, Request.STATUS.not_detected)

    def test_queue_skip_scanned(self):
        request = AttachmentRequestFactory()
        stdout = StringIO()
        self.assertEqual(Request.objects.for_object(request.content_object).count(), 1)
        call_command(
            "queue_virus_scan",
            stdout=stdout,
        )
        self.assertEqual(Request.objects.for_object(request.content_object).count(), 1)

    def test_queue_request_new(self):
        attachment = AttachmentFactory()
        stdout = StringIO()
        self.assertEqual(Request.objects.for_object(attachment).count(), 0)
        call_command(
            "queue_virus_scan",
            stdout=stdout,
        )
        self.assertEqual(Request.objects.for_object(attachment).count(), 1)
