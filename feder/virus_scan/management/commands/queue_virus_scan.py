import logging

from django.core.management.base import BaseCommand
from django.db.models import Count

from ....letters.models import Attachment
from ...models import Request as ScanRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Queue non-scanned files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, help="Count files to scan in run", default=50
        )

    def handle(self, *args, **options):
        logger.info(f"Queueing up to files {options['count']} to scan")
        scan_requests_count = ScanRequest.objects.filter(
            status=ScanRequest.STATUS.created
        ).count()
        logger.info(f"Count of files to scan: {scan_requests_count}")
        ScanRequest.objects.bulk_create(
            ScanRequest(content_object=att, field_name="attachment")
            for att in (
                Attachment.objects.annotate(req_count=Count("scan_request"))
                .filter(req_count=0)
                .exclude(letter__is_spam__in=[2, 3])
                .order_by("-id")
                .all()[: options["count"]]
            )
        )
        final_scan_requests_count = ScanRequest.objects.filter(
            status=ScanRequest.STATUS.created
        ).count()
        logger.info(
            f"Count of files to scan after queueing: {final_scan_requests_count}"
        )
