from itertools import groupby
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from guardian.models import GroupObjectPermissionBase, UserObjectPermissionBase
from guardian.shortcuts import assign_perm
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel

_('Monitorings index')
_('Can add Monitoring')
_('Can change Monitoring')
_('Can delete Monitoring')

NOTIFY_HELP = _("Notify about new alerts person who can view alerts")


class MonitoringQuerySet(models.QuerySet):
    def with_case_count(self):
        return self.annotate(case_count=models.Count('case'))


class Monitoring(TimeStampedModel):
    perm_model = 'monitoringuserobjectpermission'
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    notify_alert = models.BooleanField(default=True,
                                       verbose_name=_("Notify about alerts"),
                                       help_text=NOTIFY_HELP)
    objects = PassThroughManager.for_queryset_class(MonitoringQuerySet)()

    class Meta:
        verbose_name = _("Monitoring")
        verbose_name_plural = _("Monitoring")
        ordering = ['created', ]
        permissions = (
            ('add_questionary', _('Can add questionary')),
            ('change_questionary', _('Can change questionary')),
            ('delete_questionary', _('Can delete questionary')),
            ('add_case', _('Can add case')),
            ('change_case', _('Can change case')),
            ('delete_case', _('Can delete case')),
            ('add_task', _('Can add task')),
            ('change_task', _('Can change task')),
            ('delete_task', _('Can delete task')),
            ('add_letter', _('Can add letter')),
            ('reply', _('Can reply')),
            ('change_letter', _('Can change task')),
            ('delete_letter', _('Can delete letter')),
            ('view_alert', _('Can view alert')),
            ('change_alert', _('Can change alert')),
            ('delete_alert', _('Can delete alert')),
            ('manage_perm', _('Can manage perms')),
            ('select_survey', _('Can select answer')),
        )

    def __unicode__(self):
        return self.name

    def get_users_with_perm(self, perm=None):
        qs = get_user_model().objects.filter(**{self.perm_model + '__content_object': self})
        if perm:
            qs = qs.filter(**{self.perm_model+'__permission__codename': perm})
        return qs.distinct().all()

    def get_absolute_url(self):
        return reverse('monitorings:details', kwargs={'slug': self.slug})

    def permission_map(self):
        dataset = (self.monitoringuserobjectpermission_set.select_related('permission', 'user').
                   order_by('permission').all())
        user_list = {x.user for x in dataset}

        def index_generate():
            grouped = groupby(dataset, lambda x: x.permission)
            for perm, users in grouped:
                user_perm_list = [x.user for x in users]
                yield perm, [(perm, (user in user_perm_list)) for user in user_list]
        return user_list, index_generate()


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
        assign_perm('reply', instance.user, instance)
        assign_perm('view_alert', instance.user, instance)
        assign_perm('change_alert', instance.user, instance)
        assign_perm('delete_alert', instance.user, instance)
        assign_perm('manage_perm', instance.user, instance)
        assign_perm('select_survey', instance.user, instance)

post_save.connect(assign_default_perm, sender=Monitoring, dispatch_uid="assign_default_perm")


class MonitoringUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Monitoring)


class MonitoringGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Monitoring)
