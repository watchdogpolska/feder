from autoslug.fields import AutoSlugField
from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import Max, Prefetch, Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from feder.institutions.models import Institution
from feder.monitorings.models import Monitoring
from django.utils.timezone import datetime
from datetime import timedelta


class CaseQuerySet(models.QuerySet):
    def with_record_count(self):
        return self.annotate(record_count=models.Count("record"))

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
        from feder.records.models import Record
        from feder.letters.models import Letter

        record_queryset = (
            Record.objects.with_author()
            .exclude(letters_letters__is_spam=Letter.SPAM.spam)
            .all()
        )
        return self.prefetch_related(
            Prefetch(lookup="record_set", queryset=record_queryset)
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


class Case(TimeStampedModel):
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
        to="cases_tags.Tag", verbose_name=_("Tags"), blank=True
    )
    confirmation_received = models.BooleanField(
        verbose_name=_("Confirmation received"), default=False
    )
    response_received = models.BooleanField(
        verbose_name=_("Response received"), default=False
    )
    objects = CaseQuerySet.as_manager()

    class Meta:
        verbose_name = _("Case")
        verbose_name_plural = _("Case")
        ordering = ["created"]
        get_latest_by = "created"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("cases:details", kwargs={"slug": self.slug})

    def update_email(self):
        self.email = settings.CASE_EMAIL_TEMPLATE.format(
            pk=self.pk, domain=self.monitoring.domain.name
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
        )

    @property
    def tags_str(self):
        return " | ".join([t.name for t in self.tags.all().order_by("name")])


class Alias(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name=_("Case"))
    email = models.CharField(max_length=75, db_index=True, unique=True)
