from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from model_utils.models import TimeStampedModel
from model_utils.managers import PassThroughManager
from autoslug.fields import AutoSlugField


class MonitoringQuerySet(models.QuerySet):
    pass


class Monitoring(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    objects = PassThroughManager.for_queryset_class(MonitoringQuerySet)()
    # TODO: Define fields here

    class Meta:
        verbose_name = _("Monitoring")
        verbose_name_plural = _("Monitoring")
        ordering = ['created', ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('monitorings:details', kwargs={'slug': self.slug})

    # TODO: Define custom methods here
