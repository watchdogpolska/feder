from __future__ import unicode_literals


from django.core.management.base import BaseCommand
from django_mailbox.models import Message

from feder.letters.signals import MessageParser


class Command(BaseCommand):
    help = "Reimport mailbox archived emails as letter."

    def add_arguments(self, parser):
        parser.add_argument('limit', type=int, help="Limit of emails (default: 10)", default=10)
        parser.add_argument('--delete', dest='delete', action='store_true',
                            help="Delete messages after import.")

    def handle(self, limit, delete, *args, **options):
        for message in Message.objects.filter(letter=None).all()[:limit].iterator():
            self.stdout.write(message)
            try:
                MessageParser(message).insert()
            except IOError as e:
                print("IO error for message", message, e)
            if delete:
                message.delete()
