import logging
import time

from django.core.management.base import BaseCommand
from django.db.models import Count

from feder.virus_scan.engine import get_engine
from feder.virus_scan.models import Request

logger = logging.getLogger(__name__)
current_engine = get_engine()


class Command(BaseCommand):
    help = """
        Command to generate, send request to scan files & receive results.
        Run it in cron every 15mins.
    """

    def add_arguments(self, parser):
        parser.add_argument("--skip-generate", action="store_true")
        parser.add_argument("--skip-send", action="store_true")
        parser.add_argument("--skip-receive", action="store_true")

    def generate_requests(self):
        from ....letters.models import Attachment

        attachments_to_scan = (
            Attachment.objects.annotate(req_count=Count("scan_request"))
            .filter(req_count=0)
            .exclude(letter__is_spam__in=[2, 3])
            .exclude(attachment__isnull=True)
            .exclude(attachment__exact="")
            .order_by("id")
            .all()
        )
        valid_attachments_to_scan = [
            att
            for att in attachments_to_scan
            if att.attachment.storage.exists(att.attachment.name)
            and att.attachment.size > 0
            and bool(att.attachment.name)
        ]
        Request.objects.bulk_create(
            Request(content_object=att, field_name="attachment")
            for att in valid_attachments_to_scan
        )
        logger.info("Requests generated.")
        scan_requests_count = Request.objects.filter(
            status=Request.STATUS.created
        ).count()
        logger.info(f"Count of files to scan: {scan_requests_count}")

    def send_scan_requests(self):
        if (
            Request.objects.filter(
                status__in=[Request.STATUS.created, Request.STATUS.failed]
            ).count()
            == 0
        ):
            logger.info("No requests to send for scanning.")
            return
        for request in Request.objects.filter(
            status__in=[Request.STATUS.created, Request.STATUS.failed]
        ).order_by("-object_id")[:100]:
            logger.info(f"Send to scan: {request}")
            request.send_scan()
            request.save()
            if (
                request.status == Request.STATUS.failed
                and request.engine_report.get("error")
                and "429" in request.engine_report.get("error")
            ):
                logger.info(
                    "Too many requests sent to engine. "
                    + f"Stopping sending requests on: {request} - "
                    + request.engine_report["error"]
                )
                return
            # wait 5 sec for next request
            time.sleep(5)
        logger.info("Requests sent.")

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
        if not options["skip_receive"]:
            logger.info("Fetching scan request results not received on webhook")
            self.receive_result()
        if not options["skip_generate"]:
            logger.info("Generating requests to scan")
            self.generate_requests()
        if not options["skip_send"]:
            logger.info("Sending requests to scan")
            self.send_scan_requests()
