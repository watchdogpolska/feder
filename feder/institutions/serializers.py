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
    jst_name = serializers.CharField(source="jst.name", read_only=True)
    jst_category = serializers.CharField(source="jst.category.name", read_only=True)
    jst_voivodeship = serializers.SerializerMethodField()
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._jst_cache = {}

    def _get_jst(self, jst_id):
        """
        Gets JST instance by given id and caches the results to avoid further
        unnecessary queries.
        """
        jst = self._jst_cache.get(jst_id)
        if not jst:
            jst = JST.objects.get(id=jst_id)
            self._jst_cache[jst_id] = jst
        return jst

    def get_jst_voivodeship(self, obj):
        """
        Gets top level JST of given institution instance.
        This operation may be quite expensive.
        """
        jst = self._get_jst(obj.jst_id)
        while jst and jst.parent_id:
            jst = self._get_jst(jst.parent_id)
        return jst.name

    class Meta:
        model = Institution
        fields = (
            "pk",
            "name",
            "slug",
            "parents_ids",
            "tags",
            "jst",
            "jst_name",
            "jst_category",
            "jst_voivodeship",
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


class TagSerializer(serializers.HyperlinkedModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = ("pk", "name", "slug")
