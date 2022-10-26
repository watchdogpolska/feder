from django.urls import reverse
from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from model_utils.models import TimeStampedModel

from feder.monitorings.models import Monitoring


class TagQuerySet(models.QuerySet):
    def used(self):
        return self.annotate(case_count=Count("case")).filter(case_count__gte=1)

    def for_monitoring(self, obj):
        return self.filter(
            Q(monitoring__isnull=True) | Q(monitoring__id=obj.pk)
        ).annotate(
            cases_count=Count(
                "casetag__id", filter=Q(case__monitoring__id=obj.id), distinct=True
            )
        )


class Tag(TimeStampedModel):
    monitoring = models.ForeignKey(
        to=Monitoring,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=_("Keep blank to make global"),
    )
    name = models.CharField(max_length=250, db_index=True, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from="name", verbose_name=_("Slug"))
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if not getattr(self, "monitoring"):
            return
        return reverse(
            "cases_tags:details",
            kwargs={"monitoring": self.monitoring_id, "pk": self.pk},
        )

    class Meta:
        unique_together = [["monitoring", "name"]]
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]


class CaseTag(TimeStampedModel):
    """
    Intermediate m2m through model to allow making direct queries.
    """

    tag = models.ForeignKey(to=Tag, on_delete=models.CASCADE)
    case = models.ForeignKey(to="cases.Case", on_delete=models.CASCADE)
