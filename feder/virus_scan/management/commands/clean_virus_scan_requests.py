import logging

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from feder.letters.models import Attachment
from feder.virus_scan.engine import get_engine
from feder.virus_scan.models import Request

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
current_engine = get_engine()


class Command(BaseCommand):
    help = """
        Command to remove queued spamm attachement scan requests and update
        the scan status when result is registered in the database.
    """

    def handle(self, *args, **options):

        logger.info("Cleaning up queued scan requests for spam attachments")
        attachment_ct = ContentType.objects.get_for_model(Attachment)
        requests_to_delete = Request.objects.filter(
            content_type=attachment_ct,
            object_id__in=Attachment.objects.filter(
                letter__is_spam__in=[2, 3]
            ).values_list("id", flat=True),
            status=Request.STATUS.created,
        )
        logger.info(f"Deleting {requests_to_delete.count()} scan requests.")
        requests_to_delete.delete()
        logger.info("Scan requests for spam attachments deleted.")

        logger.info("Cleaning up scan requests for deleted attachments.")
        requests_to_delete = Request.objects.exclude(
            content_type=attachment_ct,
            object_id__in=Attachment.objects.all().values_list("id", flat=True),
        )
        logger.info(f"Deleting {requests_to_delete.count()} scan requests.")
        requests_to_delete.delete()
        logger.info("Scan requests for deleted attachments deleted.")

        logger.info("Cleaning up scan requests for attachments with file missing.")
        no_file_requests_to_delete = [
            req
            for req in Request.objects.filter(
                content_type=attachment_ct,
                object_id__in=Attachment.objects.all().values_list("id", flat=True),
            )
            if not req.get_file().storage.exists(req.get_file().name)
            or req.get_file().size == 0
            or not bool(req.get_file().name)
        ]
        logger.info(f"Deleting {len(requests_to_delete)} scan requests.")
        for req in no_file_requests_to_delete:
            req.delete()
            logger.info(f"Deleted scan request {req.id} with file missing.")
        logger.info("Scan requests for missing files deleted.")

        logger.info("Updating scan request status from results registered in DB.")
        requests_to_update = (
            Request.objects.exclude(engine_report="")
            .filter(status=Request.STATUS.failed)
            .all()
        )
        logger.info(f"{requests_to_update.count()} scan requests to update status.")
        for req in requests_to_update:
            req.status = current_engine.map_status(req.engine_report)
            req.save()
            logger.info(
                f"Updated scan request {req.id} status to {req.get_status_display()}."
            )
