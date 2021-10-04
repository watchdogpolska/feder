import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from feder.main.utils import date_random_path
from feder.institutions.models import Institution
from feder.records.models import AbstractRecord
from feder.cases.models import enforce_quarantined_queryset


class ParcelPostQuerySet(models.QuerySet):
    def for_user(self, user):
        return enforce_quarantined_queryset(self, user, "record__case")


def parcel_upload_to():
    return date_random_path("parcel")()


class AbstractParcelPost(AbstractRecord):
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    content = models.FileField(upload_to=parcel_upload_to, verbose_name=_("Content"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text=_("Created by")
    )
    objects = ParcelPostQuerySet.as_manager()

    class Meta:
        abstract = True


class IncomingParcelPost(AbstractParcelPost):
    sender = models.ForeignKey(
        to=Institution, on_delete=models.CASCADE, verbose_name=_("Sender")
    )
    comment = models.TextField(verbose_name=_("Comment"))
    receive_date = models.DateField(
        default=datetime.date.today, verbose_name=_("Receive date")
    )

    def get_absolute_url(self):
        return reverse("parcels:incoming-details", kwargs={"pk": str(self.pk)})

    def get_download_url(self):
        return reverse("parcels:incoming-download", kwargs={"pk": str(self.pk)})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Incoming parcel post")
        verbose_name_plural = _("Incoming parcel posts")


class OutgoingParcelPost(AbstractParcelPost):
    recipient = models.ForeignKey(
        to=Institution, on_delete=models.CASCADE, verbose_name=_("Recipient")
    )
    post_date = models.DateField(
        default=datetime.date.today, verbose_name=_("Post date")
    )

    def get_absolute_url(self):
        return reverse("parcels:outgoing-details", kwargs={"pk": str(self.pk)})

    def get_download_url(self):
        return reverse("parcels:outgoing-download", kwargs={"pk": str(self.pk)})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Outgoing parcel post")
        verbose_name_plural = _("Outgoing parcel posts")


@receiver(post_save, sender=IncomingParcelPost)
def update_case_statuses(sender, instance, created, raw, **kwargs):
    if not raw and created and instance.record.case_id:
        case = instance.record.case
        prev_rr = case.response_received
        case.response_received = case.get_response_received()
        if prev_rr != case.response_received:
            case.save()
