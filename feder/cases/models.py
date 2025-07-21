import uuid
from datetime import timedelta
from email.headerregistry import Address
from functools import cache

from autoslug.fields import AutoSlugField
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import CharField, Max, OuterRef, Prefetch, Q, Subquery
from django.db.models.aggregates import Aggregate
from django.db.models.functions import Cast, Trunc
from django.urls import reverse
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from feder.institutions.models import Institution
from feder.main.utils import (
    FormattedDatetimeMixin,
    RenderBooleanFieldMixin,
    get_numeric_param,
    get_param,
)
from feder.monitorings.models import Monitoring, MonitoringUserObjectPermission
from feder.teryt.models import JST


class GroupConcat(Aggregate):
    function = "GROUP_CONCAT"
    template = '%(function)s(%(distinct)s%(expressions)s SEPARATOR " | ")'


def enforce_quarantined_queryset(queryset, user, path_case):
    if user.has_perm("monitorings.view_quarantined_case"):
        return queryset
    if user.is_anonymous:
        return queryset.filter(**{f"{path_case}__is_quarantined": False})
    return queryset.filter(**{f"{path_case}__in": Case.objects.for_user(user).all()})


@cache
def get_quarantined_perm():
    ctype = ContentType.objects.get_for_model(Monitoring)
    return Permission.objects.get(content_type=ctype, codename="view_quarantined_case")


class CaseQuerySet(FormattedDatetimeMixin, models.QuerySet):
    def with_record_count(self):
        # return self.annotate(record_count=models.Count("record"))
        return self.annotate(
            record_count=models.Count(
                models.Case(
                    models.When(record__letters_letters__is_spam=2, then=None),
                    default="record",
                )
            )
        )

    def area(self, jst):
        return self.filter(
            institution__jst__tree_id=jst.tree_id,
            institution__jst__lft__range=(jst.lft, jst.rght),
        )

    def with_milestone(self):
        from feder.records.models import Record

        queryset = Record.objects.for_milestone().all()
        return self.prefetch_related(
            Prefetch(lookup="record_set", queryset=queryset, to_attr="milestone")
        )

    def with_letter(self):
        from feder.letters.models import Letter
        from feder.records.models import Record

        record_queryset = (
            Record.objects.with_author()
            .with_parcel_prefetched()
            .exclude(letters_letters__is_spam=Letter.SPAM.spam)
            .all()
        )
        return self.prefetch_related(
            Prefetch(lookup="record_set", queryset=record_queryset)
        )

    @staticmethod
    def _get_application_letter_subquery():
        from feder.letters.models import Letter

        return (
            Letter.objects.filter(
                record__case=OuterRef("pk"), author_user_id__isnull=False
            )
            .exclude_spam()
            .order_by("created")
        )

    def with_application_letter_date(self):
        return self.annotate(
            application_letter_date=Subquery(
                self._get_application_letter_subquery().values("created")[:1]
            )
        )

    def with_application_letter_status(self):
        return self.annotate(
            application_letter_status=Subquery(
                self._get_application_letter_subquery().values("emaillog__status")[:1]
            )
        )

    def with_institution(self):
        return self.select_related(
            "institution",
            "institution__jst",
            "institution__jst__parent",
            "institution__jst__parent__parent",
        )

    def by_msg(self, message):
        email_object = message.get_email_object()
        addresses = []
        addresses += message.to_addresses
        if "Envelope-To" in email_object:
            addresses += [email_object.get("Envelope-To")]
        return self.by_addresses(addresses)

    def recent(self):
        return self.filter(created__gt=datetime.now() - timedelta(days=7))

    def by_addresses(self, addresses):
        return self.filter(Q(email__in=addresses) | Q(alias__email__in=addresses))

    def with_record_max(self):
        return self.annotate(record_max=Max("record__created"))

    def with_record_max_str(self):
        return self.annotate(
            record_max_str=Cast(
                Trunc(Max("record__created"), "second"), output_field=models.CharField()
            )
        )

    def for_user(self, user):
        if user.is_anonymous:
            return self.filter(is_quarantined=False, monitoring__is_public=True)
        if user.has_perm("monitorings.view_quarantined_case"):
            return self
        non_quarantined = models.Q(is_quarantined=False)
        perm = get_quarantined_perm()
        monitoring_permission = models.Q(
            monitoring__in=MonitoringUserObjectPermission.objects.filter(
                user=user, permission=perm
            ).values("content_object")
        )
        return self.filter(non_quarantined | monitoring_permission)

    def get_mass_assign_uid(self):
        """Returns random UUID identifier ensuring it's unique."""
        while True:
            uid = uuid.uuid4()
            if not self.filter(mass_assign=uid).exists():
                return uid

    def ajax_boolean_filter(self, request, prefix, field):
        filter_values = []
        for choice in [("yes", True), ("no", False)]:
            filter_name = prefix + choice[0]
            if get_numeric_param(request, filter_name):
                filter_values.append(choice[1])
        if filter_values:
            return self.filter(**{field + "__in": filter_values})
        else:
            return self.filter(**{field + "__isnull": True})

    def ajax_area_filter(self, request):
        voivodeship_id = get_param(request, "voivodeship_filter")
        county_id = get_param(request, "county_filter")
        community_id = get_param(request, "community_filter")
        qs = self
        if community_id:
            community_filter = JST.objects.filter(pk=community_id).first()
            qs = qs.area(jst=community_filter)
        if county_id:
            county_filter = JST.objects.filter(pk=county_id).first()
            qs = qs.area(jst=county_filter)
        if voivodeship_id:
            voivodeship_filter = JST.objects.filter(pk=voivodeship_id).first()
            qs = qs.area(jst=voivodeship_filter)
        return qs

    def ajax_tags_filter(self, request):
        tags = get_param(request, "tags_filter")
        if tags:
            tag_ids = tags.split(",")
            qs = self
            for tag_id in tag_ids:
                qs = qs.filter(tags__id=tag_id)
            return qs
        return self

    def with_tags_string(self):
        return self.annotate(
            tags_string=GroupConcat(
                "tags__name", ordering="tags__name", output_field=CharField()
            )
        )


class Case(RenderBooleanFieldMixin, TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    slug = AutoSlugField(
        populate_from="name", verbose_name=_("Slug"), max_length=110, unique=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    monitoring = models.ForeignKey(
        Monitoring, on_delete=models.CASCADE, verbose_name=_("Monitoring")
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, verbose_name=_("Institution")
    )
    mass_assign = models.UUIDField(
        verbose_name="Mass assign ID", blank=True, null=True, editable=False
    )
    email = models.CharField(max_length=75, db_index=True)
    tags = models.ManyToManyField(
        to="cases_tags.Tag",
        through="cases_tags.CaseTag",
        verbose_name=_("Tags"),
        blank=True,
    )
    confirmation_received = models.BooleanField(
        verbose_name=_("Confirmation received"), default=False
    )
    response_received = models.BooleanField(
        verbose_name=_("Response received"), default=False
    )
    is_quarantined = models.BooleanField(
        verbose_name=_("Quarantined"), default=False, db_index=True
    )
    first_request = models.ForeignKey(
        "letters.Letter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="first_request",
        verbose_name=_("First request"),
    )
    last_request = models.ForeignKey(
        "letters.Letter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="last_request",
        verbose_name=_("Last request"),
    )
    objects = CaseQuerySet.as_manager()

    class Meta:
        verbose_name = _("Case")
        verbose_name_plural = _("Case")
        ordering = ["created"]
        get_latest_by = "created"
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("cases:details", kwargs={"slug": self.slug})

    def render_case_link(self):
        url = self.get_absolute_url()
        label = self.name
        bold_start = "" if self.is_quarantined else "<b>"
        bold_end = "" if self.is_quarantined else "</b>"
        return f'{bold_start}<a href="{url}">{label}</a>{bold_end}'

    def update_email(self):
        self.email = settings.CASE_EMAIL_TEMPLATE.format(
            pk=self.pk, domain=self.monitoring.domain.name
        )
        self.save()

    def get_email_address(self):
        if not self.email:
            self.update_email()
        if not self.monitoring.domain.organisation_id:
            return Address(addr_spec=self.email)
        return Address(
            display_name=self.monitoring.domain.organisation.name,
            addr_spec=self.email,
        )

    @property
    def application_letter(self):
        return (
            apps.get_model("letters", "Letter")
            .objects.filter(record__case=self, author_user_id__isnull=False)
            .order_by("created")
            .first()
        )

    def get_confirmation_received(self):
        return (
            apps.get_model("letters", "Letter")
            .objects.filter(record__case=self, author_user_id__isnull=True)
            .filter_automatic()
            .exists()
        )

    def get_response_received(self):
        return (
            apps.get_model("letters", "Letter")
            .objects.filter(record__case=self, author_user_id__isnull=True)
            .exclude_automatic()
            .exists()
        ) or (
            apps.get_model("parcels", "IncomingParcelPost")
            .objects.filter(record__case=self)
            .exists()
        )

    def get_normalized_answer(self):
        normalized_response = (
            apps.get_model("letters", "Letter")
            .objects.filter(record__case=self, author_user_id__isnull=True)
            .exclude_automatic()
            .exclude(normalized_response="")
            .exclude(normalized_response__isnull=True)
        )
        result = [
            item.get_normalized_response_html_table() for item in normalized_response
        ]
        return result

    @property
    def letter_count(self):
        return self.record_set.exclude(letters_letters__is_spam=2).count()

    @property
    def spam_count(self):
        return self.record_set.filter(letters_letters__is_spam=2).count()

    @property
    def tags_str(self):
        return " | ".join([t.name for t in self.tags.all().order_by("name")])


class Alias(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name=_("Case"))
    email = models.CharField(max_length=75, db_index=True, unique=True)
