from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from model_utils.models import TimeStampedModel
from feder.cases.models import Case
from jsonfield import JSONField
from feder.questionaries.models import Questionary, Question


class Task(TimeStampedModel):
    case = models.ForeignKey(Case)
    questionary = models.ForeignKey(Questionary)

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def get_absolute_url(self):
        return reverse('tasks:details', kwargs={'pk': self.pk})


class Survey(TimeStampedModel):
    task = models.ForeignKey(Task)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")


class Answer(models.Model):
    survey = models.ForeignKey(Survey)
    question = models.ForeignKey(Question)
    blob = JSONField()

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
