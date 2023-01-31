import django_filters
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.settings import api_settings
from teryt_tree.rest_framework_ext.viewsets import custom_area_filter

from .models import Institution, Tag
from .serializers import InstitutionSerializer, TagSerializer, InstitutionCSVSerializer
from feder.main.mixins import CsvRendererViewMixin
from feder.main.utils import PaginatedCSVStreamingRenderer


class InstitutionFilter(filters.FilterSet):
    jst = django_filters.CharFilter(method=custom_area_filter)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"

    class Meta:
        model = Institution
        fields = ["name", "tags", "jst", "regon"]


class InstitutionCSVRenderer(PaginatedCSVStreamingRenderer):
    header = [
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
    ]
    labels = {
        "pk": _("Id"),
        "name": _("Name"),
        "email": _("Email of institution"),
        "regon": _("REGON number"),
        "jst": _("JST id"),
        "jst_category": _("JST category"),
        "jst_name": _("JST name"),
        "jst_voivodeship": _("JST voivodeship"),
        "created": _("Created"),
        "modified": _("Modified"),
        "tag_names": _("Tag names"),
    }
    results_field = "results"

    def render(self, data, *args, **kwargs):
        """Copied form PaginatedCSVRenderer to support paginated results."""
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super().render(data, *args, **kwargs)


class InstitutionViewSet(CsvRendererViewMixin, viewsets.ModelViewSet):
    queryset = (
        Institution.objects.with_jst()
        .select_related("jst__category")
        .prefetch_related("tags", "parents")
        .all()
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InstitutionFilter
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (
        InstitutionCSVRenderer,
    )

    # custom attributes:
    csv_serializer = InstitutionCSVSerializer
    default_serializer = InstitutionSerializer
    csv_file_name = _("institutions")

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
