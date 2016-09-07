from rest_framework import serializers

from .models import Email, Institution, Tag


class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Email
        fields = ('pk', 'email', 'priority', 'institution')


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    on_site = serializers.CharField(source='get_absolute_url', read_only=True)
    slug = serializers.CharField(read_only=True)
    accurate_email = EmailSerializer(read_only=True)

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
