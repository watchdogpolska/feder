import django_filters
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import PaginatedCSVRenderer, CSVStreamingRenderer
from teryt_tree.rest_framework_ext.viewsets import custom_area_filter

from .models import Institution, Tag
from .serializers import InstitutionSerializer, TagSerializer, InstitutionCSVSerializer


class InstitutionFilter(filters.FilterSet):
    jst = django_filters.CharFilter(method=custom_area_filter)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"

    class Meta:
        model = Institution
        fields = ["name", "tags", "jst", "regon"]


class InstitutionCSVRenderer(CSVStreamingRenderer):
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
        return super(InstitutionCSVRenderer, self).render(data, *args, **kwargs)


class InstitutionPaginator(PageNumberPagination):
    max_page_size = (
        10000  # increased maximum page size to allow export to CSV without pagination
    )
    page_size_query_param = "page_size"


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = (
        Institution.objects.with_voivodeship()
        .select_related("jst__category")
        .prefetch_related("tags", "parents")
        .all()
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionFilter
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (
        InstitutionCSVRenderer,
    )
    pagination_class = InstitutionPaginator

    def get_serializer_class(self):
        if isinstance(self.request.accepted_renderer, InstitutionCSVRenderer):
            return InstitutionCSVSerializer
        else:
            return InstitutionSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
