from itertools import groupby

import reversion
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from guardian.models import GroupObjectPermissionBase, UserObjectPermissionBase
from model_utils.models import TimeStampedModel

from feder.domains.models import Domain
from .validators import validate_template_syntax

_("Monitorings index")
_("Can add Monitoring")
_("Can change Monitoring")
_("Can delete Monitoring")

NOTIFY_HELP = _("Notify about new alerts person who can view alerts")


class MonitoringQuerySet(models.QuerySet):
    def with_case_count(self):
        return self.annotate(case_count=models.Count("case"))

    def area(self, jst):
        return self.filter(
            case__institution__jst__tree_id=jst.tree_id,
            case__institution__jst__lft__range=(jst.lft, jst.rght),
        )

    def only_public(self):
        return self.filter(is_public=True)


@python_2_unicode_compatible
@reversion.register()
class Monitoring(TimeStampedModel):
    perm_model = "monitoringuserobjectpermission"
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    slug = AutoSlugField(populate_from="name", verbose_name=_("Slug"), unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    description = models.TextField(verbose_name=_("Description"), blank=True)
    subject = models.CharField(verbose_name=_("Subject"), max_length=80)
    template = models.TextField(
        verbose_name=_("Template"),
        help_text=_("Use {{EMAIL}} for insert reply address"),
        validators=[validate_template_syntax],
    )
    email_footer = models.TextField(
        default="",
        verbose_name=_("Email footer"),
        help_text=_("Footer for sent mail and replies"),
    )
    notify_alert = models.BooleanField(
        default=True, verbose_name=_("Notify about alerts"), help_text=NOTIFY_HELP
    )
    objects = MonitoringQuerySet.as_manager()
    is_public = models.BooleanField(default=True, verbose_name=_("Is public visible?"))
    domain = models.ForeignKey(
        to=Domain, help_text=_("Domain used to sends emails"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Monitoring")
        verbose_name_plural = _("Monitoring")
        ordering = ["created"]
        permissions = (
            ("add_questionary", _("Can add questionary")),
            ("change_questionary", _("Can change questionary")),
            ("delete_questionary", _("Can delete questionary")),
            ("add_case", _("Can add case")),
            ("change_case", _("Can change case")),
            ("delete_case", _("Can delete case")),
            ("add_task", _("Can add task")),
            ("change_task", _("Can change task")),
            ("delete_task", _("Can delete task")),
            ("add_letter", _("Can add letter")),
            ("reply", _("Can reply")),
            ("add_draft", _("Add reply draft")),
            ("change_letter", _("Can change task")),
            ("delete_letter", _("Can delete letter")),
            ("view_alert", _("Can view alert")),
            ("change_alert", _("Can change alert")),
            ("delete_alert", _("Can delete alert")),
            ("manage_perm", _("Can manage perms")),
            ("select_survey", _("Can select answer")),
            ("view_log", _("Can view logs")),
            ("spam_mark", _("Can mark spam")),
            ("add_parcelpost", _("Can add parcel post")),
            ("change_parcelpost", _("Can change parcel post")),
            ("delete_parcelpost", _("Can delete parcel post")),
            ("view_email_address", _("Can view e-mail address")),
        )

    def __str__(self):
        return self.name

    def get_users_with_perm(self, perm=None):
        qs = get_user_model().objects.filter(
            **{self.perm_model + "__content_object": self}
        )
        if perm:
            qs = qs.filter(**{self.perm_model + "__permission__codename": perm})
        return qs.distinct().all()

    def get_absolute_url(self):
        return reverse("monitorings:details", kwargs={"slug": self.slug})

    def permission_map(self):
        dataset = (
            self.monitoringuserobjectpermission_set.select_related("permission", "user")
            .order_by("permission")
            .all()
        )
        user_list = {x.user for x in dataset}

        def index_generate():
            grouped = groupby(dataset, lambda x: x.permission)
            for perm, users in grouped:
                user_perm_list = [x.user for x in users]
                yield perm, [(perm, (user in user_perm_list)) for user in user_list]

        return user_list, index_generate()


class MonitoringUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Monitoring, on_delete=models.CASCADE)


class MonitoringGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Monitoring, on_delete=models.CASCADE)
