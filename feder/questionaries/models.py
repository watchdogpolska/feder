from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from jsonfield import JSONField
from feder.questionaries.modulator import modulators

_('Questionaries index')


class Questionary(TimeStampedModel):
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    monitoring = models.ForeignKey(Monitoring, verbose_name=_("Monitoring"))
    lock = models.BooleanField(default=False, verbose_name=_("Lock of edition"),
        help_text=_("Prevent of edit question to protect against destruction the data set"))

    def get_absolute_url(self):
        return reverse('questionaries:details', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Questionary")
        verbose_name_plural = _("Questionaries")


class Question(models.Model):
    questionary = models.ForeignKey(Questionary, verbose_name=_("Questionary"))
    position = models.SmallIntegerField(default=0, verbose_name=_("Position"))
    genre = models.CharField(max_length=25, verbose_name=_("Genre"))
    blob = JSONField(verbose_name=_("Technical definition"))

    def save(self, lock_protection=True):
        # The final protection against destruction of the data set
        if lock_protection is True and self.pk is None and self.questionary.lock:
            raise ValueError("You can't modify this questionary. Some answers exists")
        return super(Question, self).save()

    def label(self):
        return modulators[self.genre](self.blob).render_label()

    class Meta:
        ordering = ['position', ]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
