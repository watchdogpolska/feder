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
            name=monitoring.name+postfix,
            monitoring=monitoring,
            institution=institution)
        case.save()
        letter = cls(author_user=user, case=case, title=monitoring.name, body=text)
        letter.save()
        letter.send()
        return letter

    def send(self):
        pass


class Attachment(AttachmentBase):
    record = models.ForeignKey(Letter)
