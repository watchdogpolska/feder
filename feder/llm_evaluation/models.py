from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from model_utils import Choices
from model_utils.models import TimeStampedModel


class LLmRequestQuerySet(models.QuerySet):
    def queued(self):
        return self.filter(status=self.model.STATUS.queued)


class LlmRequest(TimeStampedModel):
    STATUS = Choices(
        (0, "created", _("Created")),
        (1, "queued", _("Queued")),
        (2, "done", _("Done")),
        (3, "failed", _("Failed")),
    )
    engine_name = models.CharField(
        max_length=20, verbose_name=_("LLM Engine name"), null=True, blank=True
    )
    status = models.IntegerField(choices=STATUS, default=STATUS.created)
    request_prompt = models.TextField(
        verbose_name=_("LLM Engine request"), null=True, blank=True
    )
    response = models.TextField(
        verbose_name=_("LLM Engine response"), null=True, blank=True
    )
    token_usage = JSONField(
        verbose_name=_("LLM Engine token usage"), null=True, blank=True
    )
    objects = LLmRequestQuerySet.as_manager()

    class Meta:
        abstract = True


class LlmLetterRequest(LlmRequest):
    evaluated_letter = models.ForeignKey(
        "letters.Letter",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Evaluated Letter"),
    )


class LlmMonitoringRequest(LlmRequest):
    evaluated_monitoring = models.ForeignKey(
        "monitorings.Monitoring",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Evaluated Monitoring"),
    )
