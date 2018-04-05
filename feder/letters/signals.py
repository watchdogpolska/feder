import os

from cached_property import cached_property
from talon import quotations
from django.core.files import File
from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from django_mailbox.signals import message_received

from feder.alerts.models import Alert
from feder.cases.models import Case
from feder.letters.models import Attachment, Letter, logger
from feder.letters.settings import LETTER_SPAM_FUNC
from feder.records.models import Record


@receiver(post_init, sender=Attachment)
def backup_attachment_path(sender, instance, **kwargs):
    instance._current_attachment = instance.attachment


@receiver(post_save, sender=Attachment)
def delete_old_attachment(sender, instance, **kwargs):
    if hasattr(instance, '_current_attachment'):
        if instance._current_attachment != instance.attachment:
            instance._current_attachment.delete(save=False)


@receiver(post_init, sender=Letter)
def backup_eml_path(sender, instance, **kwargs):
    instance._current_eml = instance.eml


@receiver(post_save, sender=Letter)
def delete_old_eml(sender, instance, **kwargs):
    if hasattr(instance, '_current_eml'):
        if instance._current_eml != instance.eml:
            instance._current_eml.delete(save=False)


class MessageParser(object):
    def __init__(self, message, case=None):
        self.message = message
        self.case = case

    @cached_property
    def quote(self):
        if self.message.text:
            return self.message.text.replace(self.text, '')
        return self.message.text.replace(self.text, '')

    @cached_property
    def text(self):
        if self.message.text:
            return quotations.extract_from(self.message.text)
        return quotations.extract_from(self.message.html, 'text/html')

    def get_case(self):
        if self.case:
            return self.case
        try:
            self.case = Case.objects.by_msg(self.message).get()
            return self.case
        except Case.DoesNotExist:
            return

    def save_attachments(self, letter):
        # Create Letter
        attachments = []
        # Append attachments
        for attachment in self.message.attachments.all():
            name = attachment.get_filename() or 'Unknown.bin'
            if len(name) > 70:
                name, ext = os.path.splitext(name)
                ext = ext[:70]
                name = name[:70 - len(ext)] + ext
            file_obj = File(attachment.document, name)
            attachments.append(Attachment(letter=letter, attachment=file_obj))
        Attachment.objects.bulk_create(attachments)
        for att in attachments:  # Force close file descriptor to avoid "Too many open files"
            att.attachment.close()
        return attachments

    def save_object(self):
        with File(self.message.eml, self.message.eml.name) as eml:
            return Letter.objects.create(author_institution=self.case.institution,
                                         email=self.message.from_address[0],
                                         record=Record.objects.create(case=self.case),
                                         title=self.message.subject,
                                         body=self.text,
                                         quote=self.quote,
                                         eml=eml,
                                         is_draft=False,
                                         message=self.message)

    @staticmethod
    @receiver(message_received)
    def receive_signal(sender, message, **kwargs):
        MessageParser(message).insert()

    def insert(self):
        self.case = self.get_case()
        if not self.case:
            logger.warning("Message #{pk} skip, due not recognized address {to}".
                           format(pk=self.message.pk, to=self.message.to_addresses))
            return
        letter = self.save_object()
        logger.info("Message #{message} registered in case #{case} as letter #{letter}".
                    format(message=self.message.pk, case=self.case.pk, letter=letter.pk))
        attachments = self.save_attachments(letter)
        logger.debug("Saved {attachment_count} attachments for letter #{letter}".
                     format(attachment_count=len(attachments), letter=letter.pk))
        self.check_spam(letter)
        return letter

    def check_spam(self, letter):
        if LETTER_SPAM_FUNC(self.message.get_email_object()):
            Alert.objects.create(monitoring=letter.case.monitoring,
                                 reason="Auto spam detected",
                                 author=None,
                                 link_object=letter)

