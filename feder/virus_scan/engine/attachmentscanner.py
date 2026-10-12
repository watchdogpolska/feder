import requests
from django.conf import settings

from feder.virus_scan.models import Request

from .base import BaseEngine


class AttachmentScannerEngine(BaseEngine):
    name = "Attachmentscanner"

    def __init__(self):
        self.key = settings.ATTACHMENTSCANNER_API_KEY
        self.url = settings.ATTACHMENTSCANNER_API_URL
        self.session = requests.Session()

    def map_status(self, response):
        status = response.get("status")
        if status == "found":
            return Request.STATUS.infected
        # "warning" is a softer, ambiguous signal (e.g. a password-protected
        # archive the engine could not inspect) rather than a confirmed
        # malware match, so it should not block access the same way.
        if status == "warning":
            return Request.STATUS.suspicious
        if status == "ok":
            return Request.STATUS.not_detected
        if status == "pending":
            return Request.STATUS.queued
        return Request.STATUS.failed

    def send_scan(self, this_file, filename):
        resp = self.session.post(
            f"{self.url}/v0.1/scans",
            files={"file": (filename, this_file, "application/octet-stream")},
            data={"callback": self.get_webhook_url()},
            headers={"authorization": f"bearer {self.key}"},
        )
        resp.raise_for_status()
        result = resp.json()
        return {
            "engine_id": result["id"],
            "status": self.map_status(result),
            "engine_report": result,
        }

    def receive_result(self, engine_id):
        resp = self.session.get(
            f"{self.url}/v0.1/scans/{engine_id}",
            headers={"authorization": f"bearer {self.key}"},
        )
        resp.raise_for_status()
        result = resp.json()
        return {
            "engine_id": result["id"],
            "status": self.map_status(result),
            "engine_report": result,
        }
