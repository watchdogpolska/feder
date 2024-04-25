import logging
from time import sleep

from django.core.management.base import BaseCommand

from feder.virus_scan.engine import get_engine
from feder.virus_scan.models import Request

logger = logging.getLogger(__name__)
current_engine = get_engine()


class Command(BaseCommand):
    help = "Commands to send request to scan files & receive results"

    def add_arguments(self, parser):
        parser.add_argument("--skip-send", action="store_true")
        parser.add_argument("--skip-receive", action="store_true")
        parser.add_argument(
            "--delay", type=int, default=30, help="Delay between steps (in seconds)"
        )

    def send_scan(self):
        if Request.objects.filter(status=Request.STATUS.created).all().count == 0:
            logger.info("No requests to send for scanning.")
            return
        for request in Request.objects.filter(status=Request.STATUS.created).all():
            logger.info(f"Send to scan: {request}")
            request.send_scan()
            request.save()

    def receive_result(self):
        for request in (
            Request.objects.filter(status=Request.STATUS.queued)
            .filter(engine_name=current_engine.name)
            .all()
        ):
            logger.info(f"Receive result: {request}")
            request.receive_result()
            request.save()

    def handle(self, *args, **options):
        logger.info("Virus scan started.")
        if not options["skip_send"]:
            logger.info("Sending requests to scan")
            self.send_scan()
        if not options["skip_send"] and not options["skip_receive"]:
            logger.info("Delay {} seconds between steps".format(options["delay"]))
            sleep(options["delay"])
        if not options["skip_receive"]:
            logger.info("Fetching results of requests of scan")
            self.receive_result()
