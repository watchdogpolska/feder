from rest_framework import serializers

from feder.cases.models import Case


class CaseSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Case
        fields = (
            "pk",
            "name",
            "user",
            "institution",
            "monitoring",
            "created",
            "modified",
        )


class CaseReportSerializer(serializers.HyperlinkedModelSerializer):
    institution_name = serializers.SerializerMethodField()
    institution_email = serializers.SerializerMethodField()
    community = serializers.CharField(source="institution.community.name")
    county = serializers.CharField(source="institution.county.name")
    voivodeship = serializers.CharField(source="institution.voivodeship.name")
    request_date = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    response_received = serializers.SerializerMethodField()
    receiving_confirmed = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = (
            "pk",
            "institution_name",
            "institution_email",
            "community",
            "county",
            "voivodeship",
            "request_date",
            "request_status",
            "response_received",
            "receiving_confirmed",
        )

    def get_institution_name(self, obj):
        return obj.institution.name

    def get_institution_email(self, obj):
        return obj.institution.email

    def get_request_date(self, obj):
        return obj.institution.created

    def get_request_status(self, obj):
        return "?"

    def get_response_received(self, obj):
        return "?"

    def get_receiving_confirmed(self, obj):
        return "?"
