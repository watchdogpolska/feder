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
    name = models.CharField(max_length=75, verbose_name=_("Name"))
    case = models.ForeignKey(Case, verbose_name=_("Case"))
    questionary = models.ForeignKey(Questionary, verbose_name=_("Questionary"),
        help_text=_("Questionary to fill by user as task"))
    objects = PassThroughManager.for_queryset_class(TaskQuerySet)()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tasks:details', kwargs={'pk': self.pk})

    def lock_check(self):
        if self.questionary.lock is False:
            self.questionary.lock = True
            self.questionary.save()
            return True
        return False

    def save(self, lock_check=True, *args, **kwargs):
        if lock_check:
            self.lock_check()
        return super(Task, self).save(*args, **kwargs)

    class Meta:
        ordering = ['created', ]
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")


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
