import logging

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from feder.letters.models import Attachment
from feder.virus_scan.engine.attachmentscanner import AttachmentScannerEngine
from feder.virus_scan.engine.metadefender import MetaDefenderEngine
from feder.virus_scan.engine.virustotal import VirusTotalEngine
from feder.virus_scan.models import Request

logger = logging.getLogger(__name__)

ENGINE_CLASSES_BY_NAME = {
    VirusTotalEngine.name: VirusTotalEngine,
    MetaDefenderEngine.name: MetaDefenderEngine,
    AttachmentScannerEngine.name: AttachmentScannerEngine,
}

STATUS_BY_NAME = {
    "created": Request.STATUS.created,
    "queued": Request.STATUS.queued,
    "infected": Request.STATUS.infected,
    "not_detected": Request.STATUS.not_detected,
    "failed": Request.STATUS.failed,
    "suspicious": Request.STATUS.suspicious,
    "password_protected": Request.STATUS.password_protected,
}


class Command(BaseCommand):
    help = """
        Re-classify scan results against the current verdict-mapping code.

        By default, re-runs each scan request's already-stored
        engine_report through the current map_status() of the engine that
        produced it - no API calls, fast. Use this after changing how we
        *interpret* a response (e.g. the map_status logic in
        feder/virus_scan/engine/*.py) to fix attachments that were
        misclassified under the old code - most commonly ones wrongly
        marked "Infected" that should not have blocked access.

        Pass --resubmit if you instead need the provider to actually
        re-scan the file (e.g. its response schema changed, or you want a
        fresh opinion from today's AV definitions). A scanning provider's
        completed result for a given engine_id is a frozen record -
        polling it again returns the same cached data, it does not
        re-analyze the file. The only way to get a new result is to submit
        the file again, which some providers (MetaDefender) complete
        asynchronously via a webhook callback to this app, not a reply you
        can wait for inside a one-shot command. So --resubmit does not call
        the API itself: it resets the matching scan requests to "created"
        so the existing `virus_scan` pipeline (run via cron, or manually
        with `./manage.py virus_scan`) picks them up, resubmits them, and
        records the result exactly as it does for any new attachment -
        including the webhook callback path.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            default="infected",
            choices=sorted(STATUS_BY_NAME),
            help="Scan request status to act on (default: infected).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without saving anything.",
        )
        parser.add_argument(
            "--resubmit",
            action="store_true",
            help=(
                "Reset matching scan requests to 'created' so the "
                "`virus_scan` pipeline resubmits them to the provider for "
                "a fresh scan, instead of reclassifying the stored report."
            ),
        )

    def handle(self, *args, **options):
        try:
            status = STATUS_BY_NAME[options["status"]]
        except KeyError:
            raise CommandError(f"Unknown status: {options['status']}")

        if options["resubmit"]:
            self._resubmit(status, options)
        else:
            self._reclassify(status, options)

    def _resubmit(self, status, options):
        attachment_ct = ContentType.objects.get_for_model(Attachment)
        requests_to_reset = Request.objects.filter(
            content_type=attachment_ct, status=status
        )
        total = requests_to_reset.count()
        logger.info(
            f"Resetting {total} scan request(s) currently marked "
            f"'{options['status']}' to 'created' for resubmission."
        )

        if options["dry_run"]:
            for request in requests_to_reset.iterator():
                logger.info(f"[dry-run] Scan request {request.id} would be reset.")
            logger.info(
                "Done (dry-run). Run `./manage.py virus_scan` (or wait for its "
                "cron schedule) afterwards to actually resubmit them."
            )
            return

        updated = requests_to_reset.update(status=Request.STATUS.created)
        logger.info(
            f"Done. {updated} scan request(s) reset. Run `./manage.py virus_scan` "
            "(or wait for its cron schedule) to resubmit them."
        )

    def _reclassify(self, status, options):
        dry_run = options["dry_run"]

        # Instantiated lazily, only for engine names actually encountered
        # below - a deployment typically only has one engine configured,
        # and constructing an unconfigured one (e.g. VirusTotalEngine
        # without an API key) can raise.
        engines_by_name = {}

        attachment_ct = ContentType.objects.get_for_model(Attachment)
        requests_to_check = Request.objects.filter(
            content_type=attachment_ct, status=status
        ).exclude(engine_report__isnull=True)

        total = requests_to_check.count()
        logger.info(
            f"Re-classifying {total} scan request(s) currently marked "
            f"'{options['status']}' from their stored reports."
        )

        changed = 0
        skipped = 0

        for request in requests_to_check.iterator():
            engine_name = request.engine_name
            if engine_name not in engines_by_name:
                engines_by_name[engine_name] = self._build_engine(engine_name)
            engine = engines_by_name[engine_name]
            if engine is None:
                skipped += 1
                continue

            try:
                new_status = engine.map_status(request.engine_report)
            except Exception:
                logger.exception(
                    f"Scan request {request.id}: failed to re-classify, skipping."
                )
                skipped += 1
                continue

            if new_status == request.status:
                continue

            old_display = request.get_status_display()
            request.status = new_status
            new_display = request.get_status_display()
            changed += 1

            if dry_run:
                logger.info(
                    f"[dry-run] Scan request {request.id} "
                    f"({request.content_object}): {old_display} -> {new_display}"
                )
            else:
                request.save(update_fields=["status"])
                logger.info(
                    f"Scan request {request.id} "
                    f"({request.content_object}): {old_display} -> {new_display}"
                )

        logger.info(
            f"Done. {changed} changed, {skipped} skipped, "
            f"{total - changed - skipped} unchanged."
        )

    def _build_engine(self, engine_name):
        engine_cls = ENGINE_CLASSES_BY_NAME.get(engine_name)
        if engine_cls is None:
            logger.warning(f"Unknown engine '{engine_name}', skipping its requests.")
            return None
        try:
            return engine_cls()
        except Exception:
            logger.exception(
                f"Could not initialize engine '{engine_name}' (is it configured?), "
                "skipping its requests."
            )
            return None
