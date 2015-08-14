from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from jsonfield import JSONField


class Questionary(TimeStampedModel):
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    monitoring = models.ForeignKey(Monitoring, verbose_name=_("Monitoring"))
    lock = models.BooleanField(default=False, verbose_name=_("Lock"))

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Questionary")
        verbose_name_plural = _("Questionaries")

    def get_absolute_url(self):
        return reverse('questionaries:details', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.title


class Question(models.Model):
    questionary = models.ForeignKey(Questionary, verbose_name=_("Questionary"))
    position = models.SmallIntegerField(default=0, verbose_name=_("Position"))
    genre = models.CharField(max_length=25, verbose_name=_("Genre"))
    blob = JSONField(verbose_name=_("Technical definition"))

    class Meta:
        ordering = ['position', ]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
