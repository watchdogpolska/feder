import os
from datetime import datetime
from glob import glob
from django.core.management.base import BaseCommand
from feder.letters.models import Attachment
from django.conf import settings


class Command(BaseCommand):
    help = "Find orphaned attachement files - not linked to any letter"

    def add_arguments(self, parser):
        #     parser.add_argument(
        #         "--monitoring-pk", help="PK of monitoring which receive mail",
        #         required=True
        #     )
        parser.add_argument(
            "--delete",
            help="Confirm deletion of orphaned attachement",
            action="store_true",
        )

    def handle(self, *args, **options):
        orphans = []
        orphans_size = 0
        att_path = f"{settings.MEDIA_ROOT}/letters/**"
        att_files = glob(att_path, recursive=True)
        att_files.sort()
        tot_atts = len(att_files)
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Total attachement files to check: {tot_atts}")
        print(f"Options: {options}")
        print(f"Started: {start_time}")
        for count, file in enumerate(att_files):
            if os.path.isdir(file):
                print(f"{count} of {tot_atts}: {file} is directory - skipping")
                continue
            if Attachment.objects.filter(
                attachment=file.replace(settings.MEDIA_ROOT + "/", "")
            ).exists():
                print(f"{count} of {tot_atts}: attachment exists for {file}")
            else:
                file_stats = os.stat(file)
                orphans_size += file_stats.st_size
                orphans.append(file)
                print(f"{count} of {tot_atts}: attachment missing for {file}")
        print(
            "Orphaned attachments: {:,} files of {:,.2f}MB".format(
                len(orphans), orphans_size / (1024 * 1024)
            )
        )
        for att in orphans:
            if options["delete"]:
                os.remove(att)
                print(f"Deleted {att}")
            else:
                print(att)
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Completed: {end_time}")
