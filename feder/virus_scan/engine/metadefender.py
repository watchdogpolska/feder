from .base import BaseEngine
from django.conf import settings
from feder.virus_scan.models import Request
import requests


class MetaDefenderEngine(BaseEngine):
    name = "MetaDefender"

    def __init__(self):
        self.key = settings.METADEFENDER_API_KEY
        self.url = settings.METADEFENDER_API_URL
        self.session = requests.Session()
        super().__init__()

    def map_status(self, resp):
        if resp.get("status", None) == "inqueue":
            return Request.STATUS.queued
        if resp["scan_results"]["progress_percentage"] != 100:
            return Request.STATUS.queued
        if resp["scan_results"]["total_avs"] < 10:
            return Request.STATUS.failed
        if resp["scan_results"]["total_detected_avs"] > 0:
            return Request.STATUS.infected
        return Request.STATUS.not_detected

    def send_scan(self, this_file, filename):
        resp = self.session.post(
            "{}/v4/file".format(self.url),
            files={"": (filename, this_file, "application/octet-stream")},
            headers={
                "apikey": self.key,
                "filename": filename.encode("ascii", "ignore"),
                "callbackurl": self.get_webhook_url(),
            },
        )
        resp.raise_for_status()
        result = resp.json()
        return {
            "engine_id": result["data_id"],
            "status": self.map_status(result),
            "engine_report": result,
        }

    def receive_result(self, engine_id):
        resp = self.session.get(
            "{}/v4/file/{}".format(self.url, engine_id),
            headers={"apikey": self.key},
        )
        resp.raise_for_status()
        result = resp.json()
        link = "https://metadefender.opswat.com/results#!/file/{}/hash/overview".format(
            result["file_info"]["sha256"]
        )
        return {
            "engine_id": result["data_id"],
            "status": self.map_status(result),
            "engine_link": link,
            "engine_report": result,
        }
