from rest_framework import serializers

from feder.letters.models import Letter, Attachment


class NestedAttachmentSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'url': value.get_full_url(),
            'filename': value.filename
        }


class NestedLetterSerializer(serializers.HyperlinkedModelSerializer):
    author_user = serializers.StringRelatedField()
    mark_spam_by = serializers.StringRelatedField()
    attachments = NestedAttachmentSerializer(
        many=True,
        read_only=True
    )
    email_delivery_status = serializers.SerializerMethodField()
    eml = serializers.SerializerMethodField()

    def get_eml(self, obj):
        return obj.get_eml_url()

    class Meta:
        model = Letter
        fields = (
            'eml', 'author_institution', 'author_user', 'title', 'body',
            'quote', 'email', 'note',
            'is_spam', 'is_draft', 'is_incoming', 'is_outgoing',
            'email_delivery_status',
            'mark_spam_by', 'mark_spam_at',
            'eml',
            'created', 'modified',
            "attachments"
        )

    def get_email_delivery_status(self, obj):
        try:
            return obj.emaillog.status
        except Letter.emaillog.RelatedObjectDoesNotExist:
            return "unknown"
