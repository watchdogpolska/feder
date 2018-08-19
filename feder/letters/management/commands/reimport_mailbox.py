from __future__ import unicode_literals


from django.core.management.base import BaseCommand
from django_mailbox.models import Message

from feder.letters.signals import MessageParser


class Command(BaseCommand):
    help = "Reimport mailbox archived emails as letter."

    def handle(self, *args, **options):
        pass
        for message in Message.objects.filter(letter=None).all().iterator():
            self.stdout.write(message)
            try:
                MessageParser(message).insert()
            except IOError:
                message.delete()
        import ipdb;ipdb.set_trace()
