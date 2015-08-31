from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel

from feder.monitorings.models import Monitoring

ALERT_INDEX = _("Alerts index")


class AlertQuerySet(models.QuerySet):
    def monitoring(self, monitoring):
        return self.filter(monitoring=monitoring)


@python_2_unicode_compatible
class Alert(TimeStampedModel):
    monitoring = models.ForeignKey(Monitoring, verbose_name=_("Monitoring"))
    reason = models.TextField(verbose_name=_("Reason"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_("Author"),
                               related_name="alert_author",
                               null=True)
    solver = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_("Solver"),
                               related_name="alert_solver",
                               null=True)
    status = models.BooleanField(default=False, verbose_name=_("Status"))
    objects = PassThroughManager.for_queryset_class(AlertQuerySet)()

    class Meta:
        verbose_name = _("Alert")
        verbose_name_plural = _("Alerts")

    def get_status_display(self):
        return _("Open") if self.status else _("Closed")

    def __str__(self):
        return str(self.created)

    def get_absolute_url(self):
        return reverse('alerts:details', kwargs={'pk': self.pk})
