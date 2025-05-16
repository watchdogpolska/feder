import logging
import re
import time

import requests
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from feder.virus_scan.models import EngineApiKey, Request

from .base import BaseEngine

logger = logging.getLogger(__name__)


class MetaDefenderEngine(BaseEngine):
    name = "MetaDefender"

    def __init__(self):
        self.key = settings.METADEFENDER_API_KEY
        self.url = settings.METADEFENDER_API_URL
        self.session = requests.Session()
        self.get_api_key()
        super().__init__()

    def map_status(self, resp):
        status = resp.get("status")
        scan_results = resp.get("scan_results", {})
        process_info = resp.get("process_info", {})

        if status == "inqueue":
            return Request.STATUS.queued

        if scan_results.get("scan_all_result_a") == "In queue":
            return Request.STATUS.queued

        if process_info.get("progress_percentage") not in (None, 100):
            return Request.STATUS.queued

        scan_result_i = scan_results.get("scan_all_result_i")
        scan_result_a = scan_results.get("scan_all_result_a")

        if scan_result_i == 0:
            return Request.STATUS.not_detected

        if scan_result_a == "Aborted":
            return Request.STATUS.failed

        if scan_result_i and scan_result_i > 0:
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
            self.update_api_key(dict(resp.headers))
            resp.raise_for_status()
            return {
                "engine_id": result["data_id"],
                "status": self.map_status(result),
                "engine_report": result,
                "engine_link": self.get_result_url(
                    result["data_id"] if result["data_id"] is not None else None,
                ),
            }

        except requests.exceptions.HTTPError as e:
            result["error"] = str(e)
            if resp.status_code == 429:
                logger.warning(f"Rate limit hit for {filename}: {e}", exc_info=False)
            else:
                logger.error(f"HTTP error for {filename}: {e}", exc_info=False)

            return {
                "status": Request.STATUS.failed,
                "engine_report": result,
            }

        except requests.exceptions.RequestException as e:
            result = result if isinstance(result, dict) else {}
            result["error"] = str(e)
            logger.error(
                f"Failed to send request {filename}: {e}"
                + " - waiting 30 sec before sending next"
            )
            time.sleep(30)
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

    def get_api_key(self):
        available_keys = EngineApiKey.objects.filter(engine=self.name).filter(
            Q(prevention_remaining__gt=0) | Q(prevention_reset_at__lt=timezone.now())
        )
        if available_keys.exists():
            key_to_use = available_keys.first()
            self.key = key_to_use.key
            self.url = key_to_use.url
            logger.info(
                f"Using API key {key_to_use.name} for MetaDefender - "
                + f"remaining: {key_to_use.prevention_remaining} - "
                + f"available after: {key_to_use.prevention_reset_at}"
            )
        else:
            logger.warning(
                "No databse API key available for MetaDefender - using env settings."
            )

    def update_api_key(self, response_headers):
        if (
            isinstance(response_headers, dict)
            and response_headers.get("X-RateLimit-For") == "prevention_api"
        ):
            key_to_update = EngineApiKey.objects.filter(
                key=self.key, engine=self.name
            ).first()
            if key_to_update:
                key_to_update.prevention_limit = int(
                    response_headers.get("X-RateLimit-Limit", 0)
                )
                key_to_update.prevention_interval_sec = int(
                    response_headers.get("X-RateLimit-Interval", 0)
                )
                key_to_update.prevention_remaining = int(
                    response_headers.get("X-RateLimit-Remaining", 0)
                )
                key_to_update.prevention_reset_at = timezone.now() + timezone.timedelta(
                    seconds=int(
                        re.match(
                            r"(\d+)",
                            str(response_headers.get("X-RateLimit-Reset-In", 0)),
                        ).group(1)
                        if re.match(
                            r"(\d+)",
                            str(response_headers.get("X-RateLimit-Reset-In", 0)),
                        )
                        else 0
                    )
                )
                key_to_update.last_used = timezone.now()
                key_to_update.save()
                logger.info(
                    f"Updated API key {key_to_update.name} for MetaDefender - "
                    + f"remaining: {key_to_update.prevention_remaining} - "
                    + f"available after: {key_to_update.prevention_reset_at}"
                )
