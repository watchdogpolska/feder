from email import message_from_file
from os.path import dirname, join

from django_mailbox.models import Mailbox

from feder.letters.models import MessageParser


class MessageMixin(object):
    def setUp(self):
        self.mailbox = Mailbox.objects.create(from_email='from@example.com')
        super(MessageMixin, self).setUp()

    @staticmethod
    def _get_email_object(filename):  # See coddingtonbear/django-mailbox#89
        path = join(dirname(__file__), 'messages', filename)
        fp = open(path, 'rb')
        return message_from_file(fp)

    def get_message(self, filename):
        message = self._get_email_object(filename)
        msg = self.mailbox._process_message(message)
        msg.save()
        return msg

    def load_letter(self, name):
        message= self.get_message(name)
        return MessageParser(message).insert()
