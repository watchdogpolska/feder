from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


class RequestQuerySet(models.QuerySet):
    def with_content_object(self):
        return self.prefetch_related("content_object").select_related("content_type")


class Request(TimeStampedModel):
    STATUS = Choices(
        (0, "created", _("Created")),
        (1, "queued", _("Queued")),
        (2, "infected", _("Infected")),
        (3, "not_detected", _("Not detected")),
        (4, "failed", _("Failed")),
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    field_name = models.CharField(max_length=50)
    engine_name = models.CharField(
        verbose_name=_("Engine name"), max_length=20, blank=True
    )
    engine_id = models.CharField(
        max_length=100, verbose_name=_("External ID"), blank=True
    )
    engine_report = JSONField(verbose_name=_("Engine result"), blank=True)
    engine_link = models.CharField(
        max_length=150, verbose_name=_("Engine result URL"), blank=True
    )
    status = models.IntegerField(choices=STATUS, default=STATUS.created)
    objects = RequestQuerySet.as_manager()

    def get_file(self):
        return getattr(self.content_object, self.field_name)

    class Meta:
        verbose_name = _("Request of virus scan")
        verbose_name_plural = _("Requests of virus scan")
        ordering = ["created"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
