from __future__ import print_function

import logging
import os
import uuid

import claw
from atom.models import AttachmentBase
from cached_property import cached_property
from claw import quotations
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.manager import BaseManager
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_mailbox.models import Message
from django_mailbox.signals import message_received
from model_utils import Choices
from model_utils.models import TimeStampedModel

from feder.alerts.models import Alert
from feder.cases.models import Case
from feder.institutions.models import Institution
from .utils import email_wrapper

claw.init()

logger = logging.getLogger(__name__)




class LetterQuerySet(models.QuerySet):
    def attachment_count(self):
        return self.annotate(attachment_count=models.Count('attachment'))

    def with_author(self):
        return self.select_related('author_user', 'author_institution')

    def for_milestone(self):
        return self.prefetch_related('attachment_set').with_author()

    def is_outgoing(self):
        return self.filter(author_user__isnull=False)

    def is_incoming(self):
        return self.filter(author_user__isnull=True)

    def with_feed_items(self):
        return (self.with_author().
                select_related('case__institution__jst', 'case__monitoring').
                prefetch_related('attachment_set'))


class LetterManager(BaseManager.from_queryset(LetterQuerySet)):
    def get_queryset(self):
        return super(LetterManager, self).get_queryset().filter(is_spam__in=[Letter.SPAM.unknown, Letter.SPAM.non_spam])


@python_2_unicode_compatible
class Letter(TimeStampedModel):
    SPAM = Choices((0, 'unknown', _('Unknown')),
                   (1, 'spam', _('Spam')),
                   (2, 'non_spam', _('Non-spam'), ))
    case = models.ForeignKey(Case, verbose_name=_("Case"))
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author (if user)"),
                                    null=True, blank=True)
    author_institution = models.ForeignKey(Institution, verbose_name=_("Author (if institution)"),
                                           null=True, blank=True)
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    body = models.TextField(verbose_name=_("Text"))
    quote = models.TextField(verbose_name=_("Quote"), blank=True)
    email = models.EmailField(verbose_name=_("E-mail"), max_length=100, blank=True)
    note = models.TextField(verbose_name=_("Comments from editor"), blank=True)
    is_spam = models.IntegerField(choices=SPAM, default=SPAM.unknown, db_index=True)
    eml = models.FileField(upload_to="messages/%Y/%m/%d",
                           verbose_name=_("File"),
                           null=True,
                           blank=True)
    message = models.ForeignKey(Message,
                                null=True,
                                verbose_name=_("Message"),
                                help_text=_("Message registerd by django-mailbox"))
    objects = LetterManager()
    objects_with_spam = LetterQuerySet.as_manager()

    def is_spam_validated(self):
        return self.is_spam != Letter.SPAM.unknown

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")
        ordering = ['created', ]
        permissions = (
            ("can_filter_eml", _("Can filter eml")),
        )

    @property
    def is_draft(self):
        return self.is_outgoing and not bool(self.eml)

    @property
    def is_incoming(self):
        return not bool(self.author_user_id)

    @property
    def is_outgoing(self):
        return bool(self.author_user_id)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('letters:details', kwargs={'pk': self.pk})

    @property
    def author(self):
        return self.author_user if self.author_user_id else self.author_institution

    @author.setter
    def author(self, value):
        if isinstance(value, Institution):
            self.author_user = None
            self.author_institution = value
        elif isinstance(value, get_user_model()):
            self.author_institution = None
            self.author_user = value
        else:
            raise ValueError("Only User and Institution is allowed for attribute author")

    @classmethod
    def send_new_case(cls, user, monitoring, institution, text, postfix=''):
        case = Case(user=user,
                    name=monitoring.name + postfix,
                    monitoring=monitoring,
                    institution=institution)
        case.save()
        letter = cls(author_user=user,
                     case=case,
                     title=monitoring.subject,
                     body=text)
        letter.send(commit=True, only_email=False)
        return letter

    def email_body(self):
        body = self.body.replace('{{EMAIL}}', self.case.email)
        return u"{0}\n{1}".format(body, email_wrapper(self.quote))

    def _construct_message(self):
        headers = {'Return-Receipt-To': self.case.email,
                   'Disposition-Notification-To': self.case.email}
        return EmailMessage(subject=self.case.monitoring.subject,
                            from_email=self.case.email,
                            reply_to=[self.case.email],
                            to=[self.case.institution.email],
                            body=self.email_body(),
                            headers=headers)

    def send(self, commit=True, only_email=False):
        message = self._construct_message()
        text = message.message().as_bytes()
        self.email = self.case.institution.email
        self.eml.save('%s.eml' % uuid.uuid4(), ContentFile(text), save=False)
        if commit:
            self.save(update_fields=['eml', 'email'] if only_email else None)
        return message.send()


@python_2_unicode_compatible
class Attachment(AttachmentBase):
    letter = models.ForeignKey(Letter)

    def delete(self, *args, **kwargs):
        self.attachment.delete()
        super(Attachment, self).delete(*args, **kwargs)

    def __str__(self):
        if self.attachment:
            return u"{}".format(self.filename)
        return "None"


class MessageParser(object):
    def __init__(self, message):
        self.message = message

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
        try:
            return Case.objects.by_msg(self.message).get()
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
                                         case=self.case,
                                         title=self.message.subject,
                                         body=self.text,
                                         quote=self.quote,
                                         eml=eml,
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
        return letter
