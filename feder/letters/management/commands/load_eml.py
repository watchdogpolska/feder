from __future__ import unicode_literals
import argparse
from email import message_from_file

from django.core.management.base import BaseCommand
from django.utils.encoding import force_text
from django_mailbox.models import Mailbox


class Command(BaseCommand):
    help = "Import .eml files as new mail."

    def add_arguments(self, parser):

        parser.add_argument('mailbox', type=int, help="The ID of the mailbox that registers the message.")

        parser.add_argument('inputs', nargs='+', type=argparse.FileType('r'),
                            help="Message files that will be imported.")

    def handle(self, mailbox, inputs, *args, **options):
        mailbox = Mailbox.objects.get(pk=mailbox)
        for file in inputs:
            msg = message_from_file(file)
            message = mailbox.process_incoming_message(msg)
            self.stdout.write("Imported {} as {}".format(file.name, force_text(message)))
