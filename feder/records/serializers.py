from rest_framework import serializers

from feder.letters.models import Letter
from feder.letters.serializers import NestedLetterSerializer
from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost
from feder.parcels.serializers import NestedIncomingParcelPostSerializer, \
    NestedOutgoingParcelPostSerializer
from feder.records.models import Record


class RecordChildRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `tagged_object` generic relationship.
    """

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, Letter):
            return NestedLetterSerializer(value, context=self.context).data
        if isinstance(value, IncomingParcelPost):
            return NestedIncomingParcelPostSerializer(value, context=self.context).data
        if isinstance(value, OutgoingParcelPost):
            return NestedOutgoingParcelPostSerializer(value, context=self.context).data
        raise Exception('Unexpected type of related object')


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    content_object = RecordChildRelatedField(many=False, read_only=True)
    content_type = serializers.CharField(source='content_type_name')

    class Meta:
        model = Record
        fields = ('pk', 'case', 'content_object', 'content_type')
