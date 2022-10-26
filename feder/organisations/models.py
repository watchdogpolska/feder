from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class OrganisationQuerySet(models.QuerySet):
    pass


class Organisation(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    slug = AutoSlugField(
        populate_from="name", max_length=110, verbose_name=_("Slug"), unique=True
    )
    objects = OrganisationQuerySet.as_manager()

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")
        ordering = ["created"]

    def __str__(self):
        return str(self.name)
