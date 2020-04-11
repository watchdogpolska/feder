from django.core.management.base import BaseCommand, CommandError
from ...documents import LetterDocument


class Command(BaseCommand):
    def handle(self, *args, **options):
        LetterDocument.init()
        self.stdout.write(self.style.SUCCESS("Successfully created index"))
