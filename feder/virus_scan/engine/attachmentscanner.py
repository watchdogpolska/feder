from .base import BaseEngine
from django.conf import settings
from feder.virus_scan.models import Request
import requests


class AttachmentScannerEngine(BaseEngine):
    name = "Attachmentscanner"

    def __init__(self):
        self.key = settings.ATTACHMENTSCANNER_API_KEY
        self.url = settings.ATTACHMENTSCANNER_API_URL
        self.session = requests.Session()

    def map_status(self, status):
        if status in ["found", "warning"]:
            return Request.STATUS.infected
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
            "status": self.map_status(result["status"]),
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
            "status": self.map_status(result["status"]),
            "engine_report": result,
        }
