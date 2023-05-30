from time import sleep

from django.conf import settings
from virus_total_apis import PublicApi

from feder.virus_scan.models import Request

from .base import BaseEngine


class VirusTotalEngine(BaseEngine):
    name = "VirusTotal"
    delay = 60 / 4  # 4 requests of any nature per minute

    def __init__(self):
        self.client = PublicApi(settings.VIRUSTOTAL_API_KEY)

    def send_scan(self, this_file, filename):
        resp = self.client.scan_file(this_file, from_disk=False, filename=filename)
        sleep(self.delay)
        return {
            "engine_id": resp["results"]["scan_id"],
            "engine_link": resp["results"]["permalink"],
            "status": Request.STATUS.queued,
        }

    def receive_result(self, engine_id):
        resp = self.client.get_file_report(engine_id)
        sleep(self.delay)
        results = resp["results"]
        if results["response_code"] not in [1, -2]:
            raise Exception(
                "Unknown response code of VirusTotal: {}".format(resp["response_code"])
            )
        if results["response_code"] == 1 and results["total"] < 10:
            raise Exception(
                "Low level of VirusTotal scanning: {}".format(resp["total"])
            )
        result = {
            "engine_id": results["resource"],
        }
        if results["response_code"] == -2:
            result["status"] = Request.STATUS.queued
        elif results["positives"] == 0:
            result["status"] = Request.STATUS.not_detected
            result["engine_report"] = results
            result["engine_link"] = results["permalink"]
        else:
            result["status"] = Request.STATUS.infected
            result["engine_report"] = results
            result["engine_link"] = results["permalink"]

        return result
