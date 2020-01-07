import time

from django.core.management.base import BaseCommand
import requests
import json

from feder.virus_scan.engine import get_engine
from ...models import Request

current_engine = get_engine()


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument("url", help="Path to file to scan")
        parser.add_argument("--delay", help="Delay between retry", type=int, default=5)

    def handle(self, *args, **options):
        fp = requests.get(options["url"], stream=True)
        result = current_engine.send_scan(fp.raw, "data.bin")
        self.stdout.write("Registered as ID: {}".format(result["engine_id"]))
        while result["status"] == Request.STATUS.queued:
            result = current_engine.receive_result(result["engine_id"])
            self.stdout.write(
                "The file has status {} still. "
                "Awaiting {} seconds before retry.".format(
                    result["status"], options["delay"]
                )
            )
            time.sleep(options["delay"])
        self.stdout.write(
            json.dumps(result, sort_keys=True, indent=4, separators=(",", ": "))
        )
