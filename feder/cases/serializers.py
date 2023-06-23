from django.utils import formats
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from feder.cases.models import Case
from feder.letters.logs.models import EmailLog


class CaseSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Case
        fields = (
            "pk",
            "url",
            "name",
            "user",
            "institution",
            "monitoring",
            "created",
            "modified",
        )
        extra_kwargs = {"url": {"view_name": "cases:details", "lookup_field": "slug"}}


class CaseReportSerializer(serializers.HyperlinkedModelSerializer):
    institution_name = serializers.SerializerMethodField()
    institution_email = serializers.SerializerMethodField()
    institution_regon = serializers.SerializerMethodField()
    teryt = serializers.CharField(source="institution.jst.id")
    community = serializers.CharField(source="institution.community")
    county = serializers.CharField(source="institution.county")
    voivodeship = serializers.CharField(source="institution.voivodeship")
    tags = serializers.CharField(source="tags_string")
    first_request_date = serializers.SerializerMethodField()
    first_request_status = serializers.SerializerMethodField(
        label=_("first request status")
    )
    confirmation_received = serializers.SerializerMethodField()
    response_received = serializers.SerializerMethodField()
    last_request_date = serializers.SerializerMethodField()
    last_request_status = serializers.SerializerMethodField(
        label=_("last request status")
    )
    url = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = (
            "pk",
            "institution_name",
            "institution_email",
            "institution_regon",
            "voivodeship",
            "county",
            "community",
            "teryt",
            "tags",
            "first_request_date",
            "first_request_status",
            "confirmation_received",
            "response_received",
            "last_request_date",
            "last_request_status",
            "url",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get("context", {})
        request = context.get("request")
        user = request.user if request else None
        if user and not request.user.is_authenticated:
            self.fields.pop("institution_email")

    def get_institution_name(self, obj):
        return obj.institution.name

    def get_institution_email(self, obj):
        return obj.institution.email

    def get_institution_regon(self, obj):
        return obj.institution.regon

    def get_first_request_date(self, obj):
        letter = obj.first_request
        return formats.date_format(letter.created, format="Y-m-d") if letter else None

    def get_first_request_status(self, obj):
        letter = obj.first_request
        if letter:
            try:
                return letter.emaillog.status
            except EmailLog.DoesNotExist:
                pass
        return _("unknown")

    def get_last_request_date(self, obj):
        letter = obj.last_request
        return formats.date_format(letter.created, format="Y-m-d") if letter else None

    def get_last_request_status(self, obj):
        letter = obj.last_request
        if letter:
            try:
                return letter.emaillog.status
            except EmailLog.DoesNotExist:
                pass
        return _("unknown")

    def get_confirmation_received(self, obj):
        return _("yes") if obj.confirmation_received else _("no")

    def get_response_received(self, obj):
        return _("yes") if obj.response_received else _("no")

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url())
