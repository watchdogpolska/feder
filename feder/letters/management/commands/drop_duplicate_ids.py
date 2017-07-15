from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from feder.cases.models import Case


class Command(BaseCommand):
    help = "Delete the message with a duplicate ID in case."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                            help="Perform a trial run with no changes made")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def handle(self, dry_run, no_progress, *args, **options):
        self.dry_run = dry_run
        case_count, letter_count, deleted_count = 0, 0, 0
        for case in self.get_iter(self.get_queryset(), no_progress):
            ids = []
            with transaction.atomic():
                for letter in case.letter_set.select_related('message').order_by('created').all():
                    if not letter.message.message_id:  # Skip messages without Message-ID
                        continue
                    if letter.message.message_id in ids:
                        self.delete(letter)
                        deleted_count += 1
                    ids.append(letter.message.message_id)
                    letter_count += 1
            case_count += 1
        self.stdout.write("There is {} cases containing {} letters of which {} were removed.".
                          format(case_count,
                                 letter_count,
                                 deleted_count))

    def get_iter(self, qs, no_progress, **kwargs):
        if no_progress:
            return qs
        try:
            from tqdm import tqdm
        except ImportError:
            raise CommandError("Missing dependency. Please, install tqdm or use '--no-progress'")
        return tqdm(qs, total=qs.count(), file=self.stderr, **kwargs)

    def get_queryset(self):
        qs = Case.objects
        qs = qs.annotate(letter_count=Count('letter')).filter(letter_count__gt=1)  # Skip empty cases
        return qs.all()

    def delete(self, letter):
        self.stdout.write("Going  to delete message {} in case {}".format(letter.id, letter.case_id))
        if self.dry_run:
            return

        [x.attachment.delete() for x in letter.attachment_set.all()]  # Delete file
        letter.attachment_set.all().delete()  # Delete objects
        letter.eml.delete()  # Delete file

        [x.document.delete() for x in letter.message.attachments.all()]  # Delete file
        letter.message.attachments.all().delete()  # Delete objects
        letter.message.eml.delete()

        letter.message.delete()
        letter.delete()
