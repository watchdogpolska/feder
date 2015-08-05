from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from jsonfield import JSONField


class Questionary(TimeStampedModel):
    title = models.CharField(max_length=250)
    monitoring = models.ForeignKey(Monitoring)
    lock = models.BooleanField(default=False)

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Questionary")
        verbose_name_plural = _("Questionaries")

    def get_absolute_url(self):
        return reverse('questionaries:details', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.title


class Question(models.Model):
    questionary = models.ForeignKey(Questionary)
    position = models.SmallIntegerField()
    genre = models.CharField(max_length=25)
    blob = JSONField()

    class Meta:
        ordering = ['position', ]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
