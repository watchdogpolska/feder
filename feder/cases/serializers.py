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
