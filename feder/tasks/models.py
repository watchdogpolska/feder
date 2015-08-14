from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from model_utils.managers import PassThroughManager
from model_utils.models import TimeStampedModel
from feder.cases.models import Case
from jsonfield import JSONField
from feder.questionaries.models import Questionary, Question


class TaskQuerySet(models.QuerySet):
    pass


class Task(TimeStampedModel):
    name = models.CharField(max_length=75)
    case = models.ForeignKey(Case, verbose_name=_("Case"))
    questionary = models.ForeignKey(Questionary, verbose_name=_("Questionary"),
        help_text=_("Questionary to fill by user as task"))
    objects = PassThroughManager.for_queryset_class(TaskQuerySet)()

    def __unicode__(self):
        return self.name

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
