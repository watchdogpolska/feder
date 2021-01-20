from rest_framework import serializers

from feder.cases.models import Case
from feder.main.utils import void


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
    community = serializers.SerializerMethodField()
    county = serializers.SerializerMethodField()
    voivodeship = serializers.SerializerMethodField()
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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        jst = instance.institution.jst
        jst_list = [jst]

        while jst and jst.parent_id:
            jst = jst.parent
            jst_list.append(jst)
        jst_list.reverse()

        data.update(
            {
                "voivodeship": jst_list[0].name,
                "county": jst_list[1].name if len(jst_list) > 1 else None,
                "community": jst_list[2].name if len(jst_list) > 2 else None,
            }
        )
        return data

    # Following would never be called because the values are calculated in
    # to_representation although these function definitions are required
    # by serializer itself:
    get_community = void
    get_county = void
    get_voivodeship = void

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
