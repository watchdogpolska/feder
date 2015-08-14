from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from atom.models import AttachmentBase
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel
from feder.institutions.models import Institution
from feder.cases.models import Case


class LetterQuerySet(models.QuerySet):
    pass


class Letter(TimeStampedModel):
    case = models.ForeignKey(Case)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    author_institution = models.ForeignKey(Institution, null=True, blank=True)
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

    # TODO: Define custom methods here
    def author(self):
        return self.author_user if self.author_user else self.author_institution

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
