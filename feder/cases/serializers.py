from rest_framework import serializers

from feder.cases.models import Case


class CaseSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Case
        fields = (
            'pk', 'name', 'user_id', 'institution', 'monitoring',
            'created', 'modified'
        )
