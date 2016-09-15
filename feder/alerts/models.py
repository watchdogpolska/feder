from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from feder.monitorings.models import Monitoring
from model_utils.models import TimeStampedModel

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
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    link_object = GenericForeignKey('content_type', 'object_id')
    objects = AlertQuerySet.as_manager()

    class Meta:
        verbose_name = _("Alert")
        verbose_name_plural = _("Alerts")

    def get_status_display(self):
        return _("Closed") if self.status else _("Open")

    @property
    def is_closed(self):
        return self.status

    @property
    def is_open(self):
        return not self.status

    def __str__(self):
        return str(self.created)

    def get_absolute_url(self):
        return reverse('alerts:details', kwargs={'pk': self.pk})


@receiver(post_save, sender=Alert, dispatch_uid="notify_users")
def notify_users(sender, instance, created, **kwargs):
    if created and instance.monitoring.notify_alert:
        recipient_list = [x.email for x in instance.monitoring.get_users_with_perm('view_alert')]
        send_mail(subject='New alert',
                  message='in monitoring {monitoring}'.format(monitoring=instance.monitoring),
                  from_email=settings.EMAIL_NOTIFICATION,
                  recipient_list=recipient_list)
