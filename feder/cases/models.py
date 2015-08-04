from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel
from autoslug.fields import AutoSlugField
from feder.institutions.models import Institution
from feder.monitorings.models import Monitoring


class CaseQuerySet(models.QuerySet):
    def with_letter_count(self):
        return self.annotate(letter_count=models.Count('letter'))


class Case(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    monitoring = models.ForeignKey(Monitoring)
    institution = models.ForeignKey(Institution)

    # TODO: Define fields here
    objects = PassThroughManager.for_queryset_class(CaseQuerySet)()

    class Meta:
        verbose_name = _("Case")
        verbose_name_plural = _("Case")
        ordering = ['created', ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cases:details', kwargs={'slug': self.slug})
