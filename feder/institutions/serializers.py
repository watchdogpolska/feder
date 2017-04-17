from rest_framework import serializers

from feder.teryt.models import JST
from .models import Institution, Tag


class TagNestedSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        tag, _ = Tag.objects.get_or_create(name=value)
        return tag


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    on_site = serializers.CharField(source='get_absolute_url', read_only=True)
    slug = serializers.CharField(read_only=True)
    tags = TagNestedSerializer(many=True, required=False)
    jst = serializers.PrimaryKeyRelatedField(queryset=JST.objects)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        institution = Institution.objects.create(**validated_data)
        institution.tags.set(tags_data)
        return institution

    class Meta:
        model = Institution
        fields = ('pk',
                  'name',
                  'slug',
                  'tags',
                  'jst',
                  'email',
                  'on_site',)
        extra_kwargs = {
            'jst': {'view_name': 'jednostkaadministracyjna-detail'},
        }


class TagSerializer(serializers.HyperlinkedModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = ('pk', 'name', 'slug',)
