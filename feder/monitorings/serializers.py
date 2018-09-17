from rest_framework import serializers

from feder.domains.models import Domain
from feder.monitorings.models import Monitoring


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = (
            'name',
        )


class MonitoringSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='monitorings:details',
        lookup_field='slug'
    )
    domain = DomainSerializer()

    class Meta:
        model = Monitoring
        fields = (
            'pk', 'url', 'name', 'description', 'is_public', 'domain',
            'created', 'modified'
        )
