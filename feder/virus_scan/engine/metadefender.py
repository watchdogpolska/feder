import logging
import requests
from django.conf import settings

from feder.virus_scan.models import Request

from .base import BaseEngine

logger = logging.getLogger(__name__)


class MetaDefenderEngine(BaseEngine):
    name = "MetaDefender"

    def __init__(self):
        self.key = settings.METADEFENDER_API_KEY
        self.url = settings.METADEFENDER_API_URL
        self.session = requests.Session()
        super().__init__()

    def map_status(self, resp):
        # TODO review metadefender response and and status mapping
        if resp.get("status", None) == "inqueue":
            return Request.STATUS.queued
        if (
            resp.get("scan_results", None) is not None
            and resp["scan_results"].get("scan_all_result_a", None) == "In queue"
        ):
            return Request.STATUS.queued
        if (
            resp["process_info"].get("progress_percentage", None) is not None
            and resp["process_info"].get("progress_percentage", None) != 100
        ):
            return Request.STATUS.queued
        # Verbose scan result chaned in API - better to use numeric value
        # if resp["scan_results"]["scan_all_result_a"] == "No Threat Detected":
        if resp["scan_results"]["scan_all_result_i"] == 0:
            return Request.STATUS.not_detected
        if resp["scan_results"]["scan_all_result_a"] == "Aborted":
            return Request.STATUS.failed
        # if resp["scan_results"]["total_avs"] < 10:
        #     return Request.STATUS.failed
        if resp["scan_results"]["scan_all_result_i"] > 0:
            return Request.STATUS.infected
        return Request.STATUS.failed

    def get_result_url(self, engine_id):
        return f"{self.url}/v4/file/{engine_id}"

    def send_scan(self, this_file, filename):
        try:
            resp = self.session.post(
                f"{self.url}/v4/file",
                files={"": (filename, this_file, "application/octet-stream")},
                headers={
                    "apikey": self.key,
                    "filename": filename.encode("ascii", "ignore"),
                    "callbackurl": self.get_webhook_url(),
                },
            )
            result = resp.json()
            result["response_headers"] = dict(resp.headers)
            resp.raise_for_status()
            return {
                "engine_id": result["data_id"],
                "status": self.map_status(result),
                "engine_report": result,
                "engine_link": self.get_result_url(
                    result["data_id"] if result["data_id"] is not None else None,
                ),
            }
        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
            logger.error(f"Failed to send request {filename}: {e}")
            return {
                "status": Request.STATUS.failed,
                "engine_report": result,
            }

    def receive_result(self, engine_id):
        try:
            resp = self.session.get(
                self.get_result_url(engine_id),
                headers={"apikey": self.key},
            )
            resp.raise_for_status()
            result = dict(resp.json())
            result["response_headers"] = dict(resp.headers)
            return {
                "engine_id": result["data_id"],
                "status": self.map_status(result),
                "engine_report": result,
                "engine_link": self.get_result_url(
                    result["data_id"] if result["data_id"] is not None else None,
                ),
            }
        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
            logger.error(f"Failed to receive result {engine_id}: {e}")
            return {
                "status": Request.STATUS.failed,
                "engine_report": result,
            }
