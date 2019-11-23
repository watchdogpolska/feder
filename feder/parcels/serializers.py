from rest_framework import serializers

from feder.main.utils import get_full_url_for_context
from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost


class NestedAbstractParcelPostSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.StringRelatedField()
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        return get_full_url_for_context(obj.get_download_url(), self.context)


class NestedIncomingParcelPostSerializer(NestedAbstractParcelPostSerializer):
    class Meta:
        model = IncomingParcelPost
        fields = (
            "title",
            "content",
            "created_by",
            "sender",
            "comment",
            "receive_date",
            "created",
            "modified",
        )


class NestedOutgoingParcelPostSerializer(NestedAbstractParcelPostSerializer):
    class Meta:
        model = OutgoingParcelPost
        fields = (
            "title",
            "content",
            "created_by",
            "recipient",
            "post_date",
            "created",
            "modified",
        )
