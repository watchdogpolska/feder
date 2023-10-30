from itertools import groupby

import reversion
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from guardian.models import GroupObjectPermissionBase, UserObjectPermissionBase
from model_utils.models import TimeStampedModel

from feder.domains.models import Domain
from feder.main.utils import FormattedDatetimeMixin, RenderBooleanFieldMixin
from feder.teryt.models import JST

from .validators import validate_template_syntax

_("Monitorings index")
_("Can add Monitoring")
_("Can change Monitoring")
_("Can delete Monitoring")

NOTIFY_HELP = _("Notify about new alerts person who can view alerts")


class MonitoringQuerySet(FormattedDatetimeMixin, models.QuerySet):
    def with_case_count(self):
        return self.annotate(case_count=models.Count("case"))

    def with_case_confirmation_received_count(self):
        """
        function to annotate with case count
        when case.confirmation_received field is True
        """
        return self.annotate(
            case_confirmation_received_count=models.Count(
                "case", filter=models.Q(case__confirmation_received=True)
            )
        )

    def with_case_response_received_count(self):
        """
        function to annotate with case count
        when case.response_received field is True
        """
        return self.annotate(
            case_response_received_count=models.Count(
                "case", filter=models.Q(case__response_received=True)
            )
        )

    def with_case_quarantined_count(self):
        """
        function to annotate with case count
        when case.is_quarantined field is True
        """
        return self.annotate(
            case_quarantined_count=models.Count(
                "case", filter=models.Q(case__is_quarantined=True)
            )
        )

    def area(self, jst):
        return self.filter(
            case__institution__jst__tree_id=jst.tree_id,
            case__institution__jst__lft__range=(jst.lft, jst.rght),
        )

    def with_feed_item(self):
        return self.select_related("user")

    def for_user(self, user):
        if user.is_anonymous:
            return self.filter(is_public=True)
        if user.is_superuser:
            return self
        any_permission = models.Q(monitoringuserobjectpermission__user=user)
        public_only = models.Q(is_public=True)
        return self.filter(any_permission | public_only).distinct()


@reversion.register()
class Monitoring(RenderBooleanFieldMixin, TimeStampedModel):
    perm_model = "monitoringuserobjectpermission"
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    slug = AutoSlugField(
        populate_from="name", max_length=110, verbose_name=_("Slug"), unique=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    description = models.TextField(verbose_name=_("Description"), blank=True)
    subject = models.CharField(verbose_name=_("Subject"), max_length=100)
    hide_new_cases = models.BooleanField(
        default=False, verbose_name=_("Hide new cases when assigning?")
    )
    template = models.TextField(
        verbose_name=_("Template"),
        help_text=_("Use {{EMAIL}} for insert reply address"),
        validators=[validate_template_syntax],
    )
    results = models.TextField(
        default="",
        verbose_name=_("Results"),
        help_text=_("Resulrs of monitoring and received responses"),
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
            ("add_case", _("Can add case")),
            ("change_case", _("Can change case")),
            ("delete_case", _("Can delete case")),
            ("view_quarantined_case", _("Can view quarantine cases")),
            ("add_letter", _("Can add letter")),
            ("reply", _("Can reply")),
            ("add_draft", _("Add reply draft")),
            ("change_letter", _("Can change letter")),
            ("delete_letter", _("Can delete letter")),
            ("view_alert", _("Can view alert")),
            ("change_alert", _("Can change alert")),
            ("delete_alert", _("Can delete alert")),
            ("manage_perm", _("Can manage perms")),
            ("view_log", _("Can view logs")),
            ("spam_mark", _("Can mark spam")),
            ("add_parcelpost", _("Can add parcel post")),
            ("change_parcelpost", _("Can change parcel post")),
            ("delete_parcelpost", _("Can delete parcel post")),
            ("view_email_address", _("Can view e-mail address")),
            ("view_tag", _("Can view tag")),
            ("change_tag", _("Can change tag")),
            ("delete_tag", _("Can delete tag")),
            ("view_report", _("Can view report")),
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

    def render_monitoring_link(self):
        url = self.get_absolute_url()
        label = self.name
        bold_start = "" if not self.is_public else "<b>"
        bold_end = "" if not self.is_public else "</b>"
        return f'{bold_start}<a href="{url}">{label}</a>{bold_end}'

    def get_monitoring_cases_table_url(self):
        return reverse(
            "monitorings:monitoring_cases_table",
            kwargs={"slug": self.slug},
        )

    def render_monitoring_cases_table_link(self):
        url = self.get_monitoring_cases_table_url()
        label = self.name
        bold_start = "" if not self.is_public else "<b>"
        bold_end = "" if not self.is_public else "</b>"
        return f'{bold_start}<a href="{url}">{label}</a>{bold_end}'

    def generate_voivodeship_table(self):
        """
        Generate html table with monitoring voivodeships and their
        institutions and cases counts
        """
        voivodeship_list = JST.objects.filter(category__level=1).all().order_by("name")
        table = """
            <table class="table table-bordered compact" style="width: 100%">
            """
        table += """
            <tr>
                <th>Województwo</th>
                <th>Liczba spraw</th>
                <th>Liczba spraw w kwarantannie</th>
            </tr>"""
        for voivodeship in voivodeship_list:
            table += (
                "<tr><td>"
                + voivodeship.name
                + "</td><td>"
                + str(self.case_set.area(voivodeship).count())
                + "</td><td>"
                + str(
                    self.case_set.filter(is_quarantined=True).area(voivodeship).count()
                )
                + "</td></tr>"
            )
        table += "</table>"
        return table

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
