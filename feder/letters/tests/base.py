import email
from os.path import dirname, join

from django.utils import six
from django_mailbox.models import Mailbox

from feder.letters.signals import MessageParser


class MessageMixin(object):
    def setUp(self):
        self.mailbox = Mailbox.objects.create(from_email='from@example.com')
        super(MessageMixin, self).setUp()

    @staticmethod
    def _get_email_path(filename):
        return join(dirname(__file__), 'messages', filename)

    @staticmethod
    def _get_email_object(filename):  # See coddingtonbear/django-mailbox#89
        path = MessageMixin._get_email_path(filename)
        if six.PY3:
            return email.message_from_file(open(path, 'r'))
        else: # Deprecated. Back-ward compatible for PY2.7<
            return email.message_from_file(open(path, 'rb'))

    @staticmethod
    def _get_email_object_from_text(filename):  # See coddingtonbear/django-mailbox#89
        path = MessageMixin._get_email_path(filename)
        fp = open(path, 'rb')
        if six.PY3:
            return email.message_from_file(open(path, 'r'))
        else: # Deprecated. Back-ward compatible for PY2.7<
            return email.message_from_file(open(path, 'rb'))

    def get_message(self, filename):
        message = self._get_email_object(filename)
        msg = self.mailbox._process_message(message)
        msg.save()
        return msg

    def load_letter(self, name):
        message = self.get_message(name)
        return MessageParser(message).insert()
