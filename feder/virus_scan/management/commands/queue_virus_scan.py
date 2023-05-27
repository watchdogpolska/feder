from django.core.management.base import BaseCommand
from django.db.models import Count

from ....letters.models import Attachment
from ...models import Request as ScanRequest


class Command(BaseCommand):
    help = "Queue non-scanned files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, help="Count files to scan in run", default=50
        )

    def handle(self, *args, **options):
        ScanRequest.objects.bulk_create(
            ScanRequest(content_object=att, field_name="attachment")
            for att in (
                Attachment.objects.annotate(req_count=Count("scan_request"))
                .filter(req_count=0)
                .all()[: options["count"]]
            )
        )
