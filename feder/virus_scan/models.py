import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


class RequestQuerySet(models.QuerySet):
    def with_content_object(self):
        return self.prefetch_related("content_object").select_related("content_type")

    def for_object(self, obj):
        return self.filter(
            content_type=ContentType.objects.get_for_model(obj._meta.model),
            object_id=obj.pk,
        )


class Request(TimeStampedModel):
    STATUS = Choices(
        (0, "created", _("Created")),
        (1, "queued", _("Queued")),
        (2, "infected", _("Infected")),
        (3, "not_detected", _("Not detected")),
        (4, "failed", _("Failed")),
    )
    content_type = models.ForeignKey(
        ContentType, verbose_name=_("Scan of"), on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(verbose_name=_("Scan object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    field_name = models.CharField(max_length=50)
    engine_name = models.CharField(
        verbose_name=_("Engine name"), max_length=20, blank=True, null=True
    )
    engine_id = models.CharField(
        max_length=100, verbose_name=_("External ID"), blank=True, null=True
    )
    engine_report = models.JSONField(
        verbose_name=_("Engine result"), blank=True, null=True
    )
    engine_link = models.CharField(
        max_length=150, verbose_name=_("Engine result URL"), blank=True, null=True
    )
    status = models.IntegerField(choices=STATUS, default=STATUS.created)
    objects = RequestQuerySet.as_manager()

    def get_file(self):
        return getattr(self.content_object, self.field_name)

    def receive_result(self):
        from feder.virus_scan.engine import get_engine

        current_engine = get_engine()

        result = current_engine.receive_result(self.engine_id)
        for key in result:
            setattr(self, key, result[key])

    def send_scan(self):
        f = self.get_file()
        if bool(f.name) and f.storage.exists(f.name) and f.size > 0:
            from feder.virus_scan.engine import get_engine

            current_engine = get_engine()
            result = current_engine.send_scan(f.file, f.name)
            self.engine_name = current_engine.name
        else:
            logger.error(
                "File to scan is missing or 0 length: {} - {}".format(
                    self.content_object, self.field_name
                )
            )
            result = {
                "status": self.STATUS.failed,
                "engine_report": {
                    "error": "Attachement file to scan is missing or 0 length"
                },
            }
        for key in result:
            setattr(self, key, result[key])

    class Meta:
        verbose_name = _("Request of virus scan")
        verbose_name_plural = _("Requests of virus scan")
        ordering = ["created"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
