import logging

from django.core.management.base import BaseCommand

from feder.letters.logs.models import LogRecord

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        Deduplicate LogRecord instances based on the data field
        --max-id: Max ID of LogRecord instances to process.
                  Defaults to the highest ID in the database.
    """

    BATCH_SIZE = 100000
    MAX_ID = LogRecord.objects.order_by("-id").first().id

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-id",
            type=int,
            default=self.MAX_ID,
            help=(
                "Max ID of LogRecord instances to process."
                + " Defaults to the highest ID in the database."
            ),
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=self.BATCH_SIZE,
            help=(
                "Number of LogRecord instances to process per batch."
                + " Defaults to 100 000."
            ),
        )

    def handle(self, *args, **options):
        logger.info(f"Deduplicate LogRecord options: {options}")
        if options["max_id"] > self.MAX_ID:
            raise ValueError(f"--max-id cannot be greater than {self.MAX_ID}.")
        elif options["max_id"] < 1:
            raise ValueError("--max-id cannot be less than 1.")
        else:
            self.MAX_ID = options["max_id"]
        if options["batch_size"] < 1:
            raise ValueError("--batch-size cannot be less than 1.")
        else:
            self.BATCH_SIZE = options["batch_size"]
        max_id = self.BATCH_SIZE
        while max_id <= (self.MAX_ID + self.BATCH_SIZE):
            self.process_batch(max_id)
            max_id += self.BATCH_SIZE

    def process_batch(self, max_id):
        logger.info(f"Deduplicating LogRecord instances up to id={max_id}...")
        # Fetch all LogRecord instances ordered by creation time
        log_records = LogRecord.objects.filter(id__lte=max_id).order_by("id")
        total_log_records = log_records.count()
        logger.info(f"Found {total_log_records} LogRecord instances.")

        seen_data = set()
        counter = 0
        logger.info("Starting deduplication...")

        for log_record in log_records:
            # Convert JSONField to string for simplicity
            data_str = str(log_record.data)
            counter += 1
            logger.info(f"Processing log record {counter} of {total_log_records}...")

            if data_str not in seen_data:
                seen_data.add(data_str)
                logger.info(
                    "Added data_str to seen_data of unique logrecord id:"
                    + f" {log_record.id}, total unique: {len(seen_data)}."
                )
            else:
                logger.info(f"Deleting duplicate instance with id {log_record.id}.")
                log_record.delete()

        logger.info(
            self.style.SUCCESS(
                f"Deduplication completed for {total_log_records} logrecords. "
                + f"Found {len(seen_data)} unique logrecords."
            )
        )
