from autoslug.fields import AutoSlugField
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from guardian.models import GroupObjectPermissionBase, UserObjectPermissionBase
from guardian.shortcuts import assign_perm
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel

_('Monitorings index')


class MonitoringQuerySet(models.QuerySet):

    def with_case_count(self):
        return self.annotate(case_count=models.Count('case'))


class Monitoring(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    objects = PassThroughManager.for_queryset_class(MonitoringQuerySet)()

    class Meta:
        verbose_name = _("Monitoring")
        verbose_name_plural = _("Monitoring")
        ordering = ['created', ]
        permissions = (
            ('add_questionary', _('Add questionary')),
            ('change_questionary', _('Change questionary')),
            ('delete_questionary', _('Delete questionary')),
            ('add_case', _('Add case')),
            ('change_case', _('Change case')),
            ('delete_case', _('Delete case')),
            ('add_task', _('Add task')),
            ('change_task', _('Change task')),
            ('delete_task', _('Delete task')),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('monitorings:details', kwargs={'slug': self.slug})


def assign_default_perm(sender, instance, created, **kwargs):
    if created:
        assign_perm('change_monitoring', instance.user, instance)
        assign_perm('delete_monitoring', instance.user, instance)
        assign_perm('add_questionary', instance.user, instance)
        assign_perm('change_questionary', instance.user, instance)
        assign_perm('delete_questionary', instance.user, instance)
        assign_perm('add_case', instance.user, instance)
        assign_perm('change_case', instance.user, instance)
        assign_perm('delete_case', instance.user, instance)
        assign_perm('add_task', instance.user, instance)
        assign_perm('change_task', instance.user, instance)
        assign_perm('delete_task', instance.user, instance)

post_save.connect(assign_default_perm, sender=Monitoring, dispatch_uid="assign_default_perm")


class MonitoringUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Monitoring)


class MonitoringGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Monitoring)
