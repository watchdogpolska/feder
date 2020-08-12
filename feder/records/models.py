import warnings

from cached_property import cached_property

# Create your models here.
from django.db.models import Prefetch
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from django.db import models
from feder.cases.models import Case
from feder.records.registry import record_type_registry


class RecordQuerySet(models.QuerySet):
    def with_select_related_content(self):
        """
        Returns data using joins. Up to one query.
        :return: models.QuerySet
        """
        fields = [
            field.name
            for field in Record._meta.related_objects
            if issubclass(field.related_model, AbstractRecord)
        ]
        return self.select_related(*fields)

    def with_prefetch_related_content(self):
        """
        Returns data using prefetch. As many queries as different data types.
        :return:
        """
        fields = [
            field.related_name
            for field in Record._meta.related_objects
            if issubclass(field.related_model, AbstractRecord)
        ]
        return self.prefetch_related(*fields)

    def with_author(self):
        from feder.letters.models import Letter

        letter_queryset = Letter.objects.with_author().with_attachment().all()
        return self.prefetch_related(
            Prefetch(lookup="letters_letter_related", queryset=letter_queryset)
        ).all()

    def for_milestone(self):
        from feder.letters.models import Letter

        letter_queryset = Letter.objects.for_milestone().all()
        qs = self.exclude(letters_letters__is_spam=Letter.SPAM.spam)
        return qs.prefetch_related(
            Prefetch(lookup="letters_letter_related", queryset=letter_queryset)
        ).all()

    def for_api(self):
        from feder.letters.models import Letter

        letter_queryset = Letter.objects.for_api().all()
        qs = self.exclude(letters_letters__is_spam=Letter.SPAM.spam)
        return qs.prefetch_related(
            Prefetch(lookup="letters_letter_related", queryset=letter_queryset)
        ).all()


class Record(TimeStampedModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=True)
    objects = RecordQuerySet.as_manager()

    @cached_property
    def content_object(self):
        for field in Record._meta.related_objects:
            if issubclass(field.related_model, AbstractRecord) and hasattr(
                self, field.related_name
            ):
                return getattr(self, field.related_name)

    @property
    def milestone_template(self):
        warnings.warn(
            "Call to deprecated method '{}.content_template'.".format(
                self.__class__.__name__
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.type.get_template_milestone_item(self.content_object)

    @property
    def content_template(self):
        return self.type.get_template_content_item(self.content_object)

    def content_type_name(self):
        if self.content_object:
            return self.content_object._meta.model_name

    @property
    def type(self):
        return record_type_registry.get_type(self.content_object)

    class Meta:
        verbose_name = _("Record")
        verbose_name_plural = _("Records")
        ordering = ["created"]


class AbstractRecord(TimeStampedModel):
    record = models.OneToOneField(
        Record,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    @property
    def case(self):
        return self.record.case

    @case.setter
    def case(self, value):
        self.record.case = value

    class Meta:
        abstract = True
        ordering = ["created"]
