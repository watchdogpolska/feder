from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from feder.letters.models import Letter, Attachment
from feder.main.utils import get_full_url_for_context


class NestedAttachmentSerializer(serializers.HyperlinkedModelSerializer):
    filename = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_filename(self, obj):
        return obj.filename

    def get_url(self, obj):
        return obj.get_full_url()

    class Meta:
        model = Attachment
        fields = (
            'url', 'filename'
        )


class NestedLetterSerializer(serializers.HyperlinkedModelSerializer):
    author_user = serializers.StringRelatedField()
    mark_spam_by = serializers.StringRelatedField()
    attachments = serializers.SerializerMethodField()
    email_delivery_status = serializers.SerializerMethodField()
    eml = serializers.SerializerMethodField()

    def get_attachments(self, obj):
        return NestedAttachmentSerializer(
            getattr(obj, 'attachments', obj.attachment_set),
            many=True,
            read_only=True
        ).data

    def get_eml(self, obj):
        if obj.eml:
            return get_full_url_for_context(obj.get_eml_url(), self.context)

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
