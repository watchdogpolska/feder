from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
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
    status = models.BooleanField(default=False, verbose_name=_("Status"))
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    link_object = GenericForeignKey('content_type', 'object_id')
    objects = PassThroughManager.for_queryset_class(AlertQuerySet)()

    class Meta:
        verbose_name = _("Alert")
        verbose_name_plural = _("Alerts")

    def get_status_display(self):
        return _("Closed") if self.status else _("Open")

    def __str__(self):
        return str(self.created)

    def get_absolute_url(self):
        return reverse('alerts:details', kwargs={'pk': self.pk})


def notify_users(sender, instance, created, **kwargs):
    if created and instance.monitoring.notify_alert:
        recipient_list = [x.email for x in instance.monitoring.get_users_with_perm('view_alert')]
        send_mail(subject='New alert',
                  message='in monitoring {monitoring}'.format(monitoring=instance.monitoring),
                  from_email=settings.EMAIL_NOTIFICATION,
                  recipient_list=recipient_list)
post_save.connect(notify_users, sender=Alert, dispatch_uid="notify_users")
