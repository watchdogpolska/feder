import uuid

from atom.models import AttachmentBase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel

from feder.cases.models import Case
from feder.institutions.models import Institution


class LetterQuerySet(models.QuerySet):
    def attachment_count(self):
        return self.annotate(attachment_count=models.Count('attachment'))

    def for_milestone(self):
        return (self.prefetch_related('attachment_set').
                select_related('author_user', 'author_institution'))

    def is_outgoing(self):
        return self.filter(author_user__isnull=False)

    def is_incoming(self):
        return self.filter(author_user__isnull=True)


@python_2_unicode_compatible
class Letter(TimeStampedModel):
    case = models.ForeignKey(Case, verbose_name=_("Case"))
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author (if user)"),
                                    null=True, blank=True)
    author_institution = models.ForeignKey(Institution, verbose_name=_("Author (if institution)"),
                                           null=True, blank=True)
    title = models.CharField(verbose_name=_("Title"), max_length=50)
    body = models.TextField(verbose_name=_("Text"))
    quote = models.TextField(verbose_name=_("Quote"), blank=True)
    email = models.EmailField(verbose_name=_("E-mail"), max_length=50, blank=True)
    objects = PassThroughManager.for_queryset_class(LetterQuerySet)()
    eml = models.FileField(upload_to="messages/%Y/%m/%d",
                           verbose_name=_("File"),
                           null=True)

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")
        ordering = ['created', ]
        permissions = (
            ("can_filter_eml", _("Can filter eml")),
        )

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
        letter = cls(author_user=user, case=case, title=monitoring.name, body=text)
        letter.send(commit=True, only=False)
        return letter

    def email_body(self):
        return self.body.replace('{{EMAIL}}', self.case.email or '')

    def _construct_message(self):
        return EmailMessage(subject=self.case.monitoring,
                            from_email=self.case.email,
                            reply_to=[self.case.email],
                            to=[self.case.institution.address],
                            body=self.email_body())

    def send(self, commit=True, only=False):
        message = self._construct_message()
        text = message.message().as_bytes()
        self.email = self.case.institution.address
        self.eml.save('%s.eml' % uuid.uuid4(), ContentFile(text), save=False)
        if commit:
            self.save(update_fields=['eml', 'email'] if only else None)
        return message.send()


class Attachment(AttachmentBase):
    record = models.ForeignKey(Letter)
