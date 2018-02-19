from __future__ import print_function

import logging
import uuid

import talon
from atom.models import AttachmentBase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.mail.message import make_msgid
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_mailbox.models import Message
from model_utils import Choices
from model_utils.models import TimeStampedModel
from feder.cases.models import Case
from feder.institutions.models import Institution
from .utils import email_wrapper, normalize_msg_id

talon.init()

logger = logging.getLogger(__name__)


class LetterQuerySet(models.QuerySet):
    def attachment_count(self):
        return self.annotate(attachment_count=models.Count('attachment'))

    def with_author(self):
        return self.select_related('author_user', 'author_institution')

    def for_milestone(self):
        return self.prefetch_related('attachment_set').with_author()

    def is_draft(self):
            return self.filter(is_draft=True).is_outgoing()

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
    mark_spam_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name=_("Spam marker"),
                                     help_text=_("The person who marked it as spam"),
                                     related_name="letter_mark_spam_by")
    mark_spam_at = models.DateTimeField(null=True, verbose_name="Time of mark as spam",
                                        help_text=_("Time when letter was marked as spam"))

    is_draft = models.BooleanField(verbose_name=_("Is draft?"), default=True)

    mark_hidden_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name=_("Hiding person"),
                                       help_text=_("The person who hid the letter"),
                                       related_name="letter_mark_hidden_by")

    message_id_header = models.CharField(blank=True,
                                         verbose_name=_('ID of sent email message "Message-ID"'),
                                         max_length=500)
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
            ("recognize_letter", _("Can recognize letter"))
        )

    @property
    def is_incoming(self):
        return not bool(self.author_user_id)

    @property
    def is_outgoing(self):
        return bool(self.author_user_id)

    @property
    def is_hidden(self):
        return bool(self.mark_hidden_by_id)

    def get_title(self):
        if self.title and self.title.strip():
            return self.title
        return _("(no subject)")

    def __str__(self):
        return unicode(self.get_title())

    def __unicode__(self):
        return unicode(self.get_title())

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
        body = self.add_footer(body)
        return u"{0}\n{1}".format(body, email_wrapper(self.quote))

    def add_footer(self, body):
        footer = self.case.monitoring.email_footer
        if footer and footer.strip():
            return u"{0}\n\n--\n{1}".format(body, footer)
        else:
            return body

    def _construct_message(self, msg_id=None):
        headers = {'Return-Receipt-To': self.case.email,
                   'Disposition-Notification-To': self.case.email,
                   }
        if msg_id:
            headers['Message-ID'] = msg_id
        return EmailMessage(subject=self.case.monitoring.subject,
                            from_email=self.case.email,
                            reply_to=[self.case.email],
                            to=[self.case.institution.email],
                            body=self.email_body(),
                            headers=headers)

    def send(self, commit=True, only_email=False):
        msg_id = make_msgid(domain=self.case.email.split('@', 2)[1])
        message = self._construct_message(msg_id=msg_id)
        text = message.message().as_bytes()
        self.email = self.case.institution.email
        self.message_id_header = normalize_msg_id(msg_id)
        self.eml.save('%s.eml' % uuid.uuid4(), ContentFile(text), save=False)
        self.is_draft = False
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


