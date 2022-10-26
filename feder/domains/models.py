from feder.organisations.models import Organisation
from django.db import models

from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class DomainQuerySet(models.QuerySet):
    def for_user(self, user):
        return self


class Domain(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    active = models.BooleanField(default=True, help_text=_("Activity status"))
    organisation = models.ForeignKey(
        to=Organisation,
        verbose_name=_("Organisation"),
        on_delete=models.CASCADE,
        null=True,  # TODO(ad-m): make field required after data migration
    )
    objects = DomainQuerySet.as_manager()

    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
        ordering = ["created"]

    def __str__(self):
        return self.name
