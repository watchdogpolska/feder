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
        logger.info("Scan requests deleted.")
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
