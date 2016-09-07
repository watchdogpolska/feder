from rest_framework import serializers

from .models import Email, Institution, Tag
from feder.teryt.models import JST


class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Email
        fields = ('pk', 'email', 'priority', 'institution')


class EmailNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('pk', 'email', 'priority')


class TagNestedSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        tag, _ = Tag.objects.get_or_create(name=value)
        return tag


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    on_site = serializers.CharField(source='get_absolute_url', read_only=True)
    slug = serializers.CharField(read_only=True)
    accurate_email = EmailSerializer(read_only=True)
    tags = TagNestedSerializer(many=True, required=False)
    email_set = EmailNestedSerializer(many=True, required=False)
    jst = serializers.PrimaryKeyRelatedField(queryset=JST.objects)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        emails_data = validated_data.pop('email_set', [])
        institution = Institution.objects.create(**validated_data)
        institution.tags.set(tags_data)
        for email_data in emails_data:
            Email.objects.create(institution=institution, **email_data)
        return institution

    class Meta:
        model = Institution
        fields = ('pk',
                  'name',
                  'slug',
                  'tags',
                  'accurate_email',
                  'jst',
                  'email_set',
                  'on_site',)
        extra_kwargs = {
            'jst': {'view_name': 'jednostkaadministracyjna-detail'},
        }


class TagSerializer(serializers.HyperlinkedModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = ('pk', 'name', 'slug', )
