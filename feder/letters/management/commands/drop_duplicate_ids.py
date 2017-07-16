from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from feder.cases.models import Case


class Command(BaseCommand):
    help = "Delete the message with a duplicate ID in case."

    def add_arguments(self, parser):
        parser.add_argument('--delete', dest='delete', action='store_true',
                            help="Really delete messages.")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def handle(self, delete, no_progress, *args, **options):
        self.delete = delete
        self.no_progress = no_progress
        case_count, letter_count, deleted_count = 0, 0, 0
        for case in self.get_iter(self.get_queryset()):
            ids = []
            with transaction.atomic():
                for letter in case.letter_set.select_related('message').order_by('created').all():
                    letter_count += 1
                    if not letter.message or not letter.message.message_id:  # Skip messages without Message-ID
                        continue
                    if letter.message.message_id in ids:
                        self.delete_letter(letter)
                        deleted_count += 1
                    ids.append(letter.message.message_id)
            case_count += 1
        self.stdout.write("There is {} cases containing {} letters of which {} {} removed.".
                          format(case_count,
                                 letter_count,
                                 deleted_count,
                                 'were' if self.delete else 'will be'))

    def get_iter(self, qs, **kwargs):
        if not self.no_progress:
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

    def delete_letter(self, letter):
        if not self.no_progress:
            self.stdout.write("Going  to delete letter {} in case {}".format(letter.id, letter.case_id))

        if not self.delete:
            return

        [x.attachment.delete() for x in letter.attachment_set.all()]  # Delete file
        letter.attachment_set.all().delete()  # Delete objects
        letter.eml.delete()  # Delete file

        [x.document.delete() for x in letter.message.attachments.all()]  # Delete file
        letter.message.attachments.all().delete()  # Delete objects
        letter.message.eml.delete()

        letter.message.delete()
        letter.delete()
