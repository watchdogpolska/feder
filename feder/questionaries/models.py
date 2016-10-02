from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from model_utils.models import TimeStampedModel

from feder.monitorings.models import Monitoring

from .modulator import modulators

_('Questionaries index')

LOCK_HELP = _("Prevent of edit question to protect against destruction the data set")


@python_2_unicode_compatible
class Questionary(TimeStampedModel):
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    monitoring = models.ForeignKey(Monitoring, verbose_name=_("Monitoring"))
    lock = models.BooleanField(default=False, verbose_name=_("Lock of edition"),
                               help_text=LOCK_HELP)

    def get_absolute_url(self):
        return reverse('questionaries:details', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Questionary")
        verbose_name_plural = _("Questionaries")


@python_2_unicode_compatible
class Question(models.Model):
    questionary = models.ForeignKey(Questionary, verbose_name=_("Questionary"))
    position = models.SmallIntegerField(default=0, verbose_name=_("Position"))
    genre = models.CharField(max_length=25, verbose_name=_("Genre"))
    definition = JSONField(verbose_name=_("Technical definition"))

    def get_absolute_url(self):
        return reverse('questionaries:question_update', kwargs={'pk': self.pk})

    @property
    def is_configured(self):
        return bool(self.definition)

    @property
    def modulator(self):
        return modulators[self.genre]()

    def __str__(self):
        if not self.is_configured:
            return _("Undefined question - {description}").format(
                description=self.modulator.description)
        return self.modulator.get_label_text(self.definition)

    class Meta:
        ordering = ['position', ]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
