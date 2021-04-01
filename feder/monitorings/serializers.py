from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from feder.cases.models import Case
from feder.cases_tags.models import Tag, CaseTag
from feder.domains.models import Domain
from feder.monitorings.models import Monitoring


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ("name",)


class MonitoringSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="monitorings:details", lookup_field="slug"
    )
    domain = DomainSerializer()

    class Meta:
        model = Monitoring
        fields = (
            "pk",
            "url",
            "name",
            "description",
            "is_public",
            "domain",
            "created",
            "modified",
        )


class MultiCaseTagSerializer(serializers.Serializer):
    OPERATIONS = Choices((1, "add", _("Add")), (2, "remove", _("Remove")))

    cases = serializers.PrimaryKeyRelatedField(
        required=True, many=True, queryset=Case.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        required=True, many=True, queryset=Tag.objects.all()
    )
    operation = serializers.ChoiceField(choices=OPERATIONS, required=True)

    def validate_cases(self, cases):
        errors = []
        for case in cases:
            if case.monitoring != self._monitoring:
                errors.append(
                    "Case {} does not belong to monitoring {}".format(
                        case, self._monitoring
                    )
                )
        if errors:
            raise ValidationError(errors)
        return cases

    def validate_tags(self, tags):
        errors = []
        for tag in tags:
            if tag.monitoring and tag.monitoring != self._monitoring:
                errors.append(
                    "Tag {} does not belong to monitoring {}".format(
                        tag, self._monitoring
                    )
                )
        if errors:
            raise ValidationError(errors)
        return tags

    def __init__(self, monitoring, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._monitoring = monitoring

    @transaction.atomic
    def save(self):
        data = self.validated_data

        if data["operation"] == self.OPERATIONS.add:
            for case in data["cases"]:
                case.tags.add(*data["tags"])
                case.save()

        elif data["operation"] == self.OPERATIONS.remove:
            CaseTag.objects.filter(
                case__id__in=[c.id for c in data["cases"]],
                tag__id__in=[t.id for t in data["tags"]],
            ).delete()

        else:
            raise Exception("Unsupported operation")

        return
