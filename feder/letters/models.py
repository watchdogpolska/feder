from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from atom.models import AttachmentBase
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel
from feder.institutions.models import Institution
from feder.cases.models import Case


class LetterQuerySet(models.QuerySet):

    def for_milestone(self):
        return (self.prefetch_related('attachment_set').
                select_related('author_user', 'author_institution'))


class Letter(TimeStampedModel):
    case = models.ForeignKey(Case, verbose_name=_("Case"))
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author (if user)"),
                                    null=True, blank=True)
    author_institution = models.ForeignKey(Institution, verbose_name=_("Author (if institution)"),
                                           null=True, blank=True)
    title = models.CharField(verbose_name=_("Title"), max_length=50)
    body = models.TextField(verbose_name=_("Text"))
    quote = models.TextField(verbose_name=_("Quote"), blank=True)
    # TODO: Define fields here
    objects = PassThroughManager.for_queryset_class(LetterQuerySet)()
    eml = models.FileField(upload_to="messages/%Y/%m/%d",
                           verbose_name=_("File"),
                           null=True)

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")
        ordering = ['created', ]

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('letters:details', kwargs={'pk': self.pk})

    @property
    def author(self):
        return self.author_user if self.author_user_id else self.author_institution

    @author.setter
    def author(self, value):
        if isinstance(value, Institution):
            self.author_institution = value
        elif isinstance(value, get_user_model()):
            self.author_user = value
        raise ValueError("Only User and Institution is allowed for attribute author")

    @classmethod
    def send_new_case(cls, user, monitoring, institution, text, postfix=''):
        case = Case(user=user,
                    name=monitoring.name + postfix,
                    monitoring=monitoring,
                    institution=institution)
        case.save()
        letter = cls(author_user=user, case=case, title=monitoring.name, body=text)
        letter.send(commit=True)
        return letter

    def email_body(self):
        return self.body.replace('{{EMAIL}}', self.case.email)

    def _construct_message(self):
        return EmailMessage(subject=self.case.monitoring,
                            from_email=self.case.get_email(),
                            reply_to=[self.case.get_email()],
                            to=[self.case.institution.address],
                            body=self.case.email)

    def send(self, commit=True):
        self.eml = self._construct_message()
        r = self.eml.send()
        if commit:
            self.save()
        return r


class Attachment(AttachmentBase):
    record = models.ForeignKey(Letter)
