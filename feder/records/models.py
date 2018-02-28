# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cached_property import cached_property
from django.db import models

# Create your models here.
from django.db.models import Prefetch
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from django.db import models
from feder.cases.models import Case


class RecordQuerySet(models.QuerySet):
    def with_all_related(self):
        fields = [field.related_name for field in Record._meta.related_objects if
                  issubclass(field.related_model, AbstractRecord)]
        return self.select_related(fields)

    def with_author(self):
        from feder.letters.models import Letter
        letter_queryset = Letter.objects.with_author().all()
        return self.prefetch_related(Prefetch(lookup='letters_letter_related', queryset=letter_queryset)).all()

    def for_milestone(self):
        from feder.letters.models import Letter
        letter_queryset = Letter.objects.for_milestone().all()
        qs = self.filter(letters_letters__is_spam__in=[Letter.SPAM.unknown, Letter.SPAM.non_spam])
        return qs.prefetch_related(Prefetch(lookup='letters_letter_related',
                                            queryset=letter_queryset)).all()


class Record(TimeStampedModel):
    case = models.ForeignKey(Case)
    objects = RecordQuerySet.as_manager()

    @cached_property
    def content_object(self):
        for field in Record._meta.related_objects:
            if issubclass(field.related_model, AbstractRecord) and hasattr(self, field.related_name):
                return getattr(self, field.related_name)

    @cached_property
    def content_template(self):
        return "%s/%s%s.html" % (
            self.content_object._meta.app_label,
            self.content_object._meta.model_name,
            "_milestone_item"
        )

    class Meta:
        verbose_name = _("Record")
        verbose_name_plural = _("Records")
        ordering = ['created', ]


class AbstractRecord(TimeStampedModel):
    record = models.OneToOneField(
        Record,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    @property
    def case(self):
        return self.record.case

    class Meta:
        abstract = True
        ordering = ['created', ]
