from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from feder.teryt.models import JST
from .models import Institution, Tag


class TagNestedSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        tag, _ = Tag.objects.get_or_create(name=value)
        return tag


class ParentSerializer(serializers.HyperlinkedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="institution-detail")

    class Meta:
        model = Institution
        fields = ("pk", "self", "name", "regon", "created", "modified")


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="institutions:details", lookup_field="slug"
    )
    self = serializers.HyperlinkedIdentityField(
        view_name="institution-detail",
        # lookup_field='pk'
    )
    regon = serializers.CharField(
        validators=[UniqueValidator(queryset=Institution.objects.all())], required=False
    )
    slug = serializers.CharField(read_only=True)
    tags = TagNestedSerializer(many=True, required=False)
    parents = ParentSerializer(many=True, read_only=True)
    parents_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        read_only=False,
        queryset=Institution.objects.all(),
        source="parents",
    )
    jst = serializers.PrimaryKeyRelatedField(queryset=JST.objects)
    extra = serializers.JSONField(required=False)

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        parents_data = validated_data.pop("parents", [])
        institution = Institution.objects.create(**validated_data)
        institution.tags.set(tags_data)
        institution.parents.set(parents_data)
        return institution

    def update(self, instance, validated_data):
        if "parents" in validated_data:
            instance.parents.set(validated_data["parents"])
        return super().update(instance, validated_data)

    class Meta:
        model = Institution
        fields = (
            "pk",
            "name",
            "slug",
            "parents_ids",
            "tags",
            "jst",
            "email",
            "url",
            "regon",
            "self",
            "parents",
            "extra",
            "created",
            "modified",
        )
        extra_kwargs = {"jst": {"view_name": "jednostkaadministracyjna-detail"}}


class InstitutionCSVSerializer(InstitutionSerializer):
    jst_name = serializers.CharField(source="jst.name", read_only=True)
    jst_category = serializers.CharField(source="jst.category.name", read_only=True)
    jst_voivodeship = serializers.CharField(source="voivodeship.name", read_only=True)
    tag_names = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta(InstitutionSerializer.Meta):
        fields = (
            "pk",
            "name",
            "email",
            "regon",
            "jst",
            "jst_category",
            "jst_name",
            "jst_voivodeship",
            "created",
            "modified",
            "tag_names",
        )

    def get_tag_names(self, obj):
        return " | ".join(t.name for t in obj.tags.all())


class TagSerializer(serializers.HyperlinkedModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = ("pk", "name", "slug")
