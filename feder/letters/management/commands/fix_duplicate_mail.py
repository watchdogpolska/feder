from django.core.management.base import BaseCommand
from feder.monitorings.models import Monitoring
from feder.letters.models import Letter
from io import BytesIO
import email
import gzip


class Command(BaseCommand):
    help = "Remove duplicated incoming letters based on 'Message-ID'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--monitoring-pk", help="PK of monitoring which receive mail", required=True
        )
        parser.add_argument(
            "--delete", help="Confirm deletion of email", action="store_true"
        )

    def handle(self, *args, **options):
        monitoring = Monitoring.objects.get(pk=options["monitoring_pk"])
        for case in monitoring.case_set.all():
            ids = set()
            for letter in (
                Letter.objects.filter(record__case=case.pk).is_incoming().all()
            ):
                self.stdout.write(f"Processing letter: {letter.pk}")
                if not letter.eml:
                    self.stdout.write(f"Skipping {letter.pk} due missing eml.")
                    continue
                content = letter.eml.file.read()
                fp = BytesIO(content)
                if b"Subject:" not in content:
                    fp = gzip.GzipFile(fileobj=fp)
                msg = email.message_from_binary_file(fp)
                msg_id = msg.get("Message-ID")
                if not msg_id:
                    self.stdout.write(
                        f"Skipping {letter.pk} due missing 'Message-ID'."
                    )
                    continue
                if msg_id not in ids:
                    self.stdout.write(
                        "Skipping {} due unique 'Message-ID': {}".format(
                            letter.pk, msg_id
                        )
                    )
                    ids.add(msg_id)
                    continue
                self.stdout.write(
                    "Removing {} due duplicated 'Message-ID': {}".format(
                        letter.pk, msg_id
                    )
                )
                if options["delete"]:
                    letter.delete()
