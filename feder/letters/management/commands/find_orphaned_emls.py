import os
from datetime import datetime
from django.core.management.base import BaseCommand
from feder.letters.models import Letter
from django.conf import settings
from glob import glob


class Command(BaseCommand):
    help = "Find orphaned eml files - not linked to any letter"

    def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--monitoring-pk", help="PK of monitoring which receive mail",
    #         required=True
    #     )
        parser.add_argument(
            "--delete",
            help="Confirm deletion of orphaned eml",
            action="store_true"
        )

    def handle(self, *args, **options):
        orphans = []
        orphans_size = 0
        msg_path = f"{settings.MEDIA_ROOT}/messages/**"
        msg_files = glob(msg_path, recursive=True)
        msg_files.sort()
        tot_emls = len(msg_files)
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"total message files to check: {tot_emls}")
        print(f'Options: {options}')
        print(f"Started: {start_time}")
        for count, file in enumerate(msg_files):
            if os.path.isdir(file):
                print(f"{count} of {tot_emls}: {file} is directory - skipping")
                continue
            if Letter.objects.filter(
                eml=file.replace(settings.MEDIA_ROOT + "/", "")
            ).exists():
                print(f"{count} of {tot_emls}: letter exists for {file}")
            else:
                file_stats = os.stat(file)
                orphans_size += file_stats.st_size
                orphans.append(file)
                print(f"{count} of {tot_emls}: letter missing for {file}")
        print(
            "Orphaned emls: {:,} files of {:,.2f}MB".format(
                len(orphans), orphans_size / (1024 * 1024)
            )
        )
        for eml in orphans:
            if options["delete"]:
                os.remove(eml)
                print(f"Deleted {eml}")
            else:
                print(eml) 
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Completed: {end_time}")
