import django_filters
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import PaginatedCSVRenderer
from teryt_tree.rest_framework_ext.viewsets import custom_area_filter

from .models import Institution, Tag
from .serializers import InstitutionSerializer, TagSerializer


class InstitutionFilter(filters.FilterSet):
    jst = django_filters.CharFilter(method=custom_area_filter)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"

    class Meta:
        model = Institution
        fields = ["name", "tags", "jst", "regon"]


class InstitutionCSVRenderer(PaginatedCSVRenderer):
    header = [
        "pk", "name", "email", "jst", "jst_name", "jst_voivodeship", "jst_category", "created", "modified", "regon",
        "self", "slug", "tags.0", "url"
    ]
    labels = {
        "pk": _("Primary key"),
        "name": _("Name"),
        "email": _("Email of institution"),
        "jst": _("JST id"),
        "jst_name": _("JST name"),
        "jst_category": _("JST category"),
        "jst_voivodeship": _("JST voivodeship"),
        "created": _("Created"),
        "modified": _("Modified"),
        "regon": _("REGON number"),
        "self": _("Parent institutions"),
        "slug": _("Slug"),
        "tags.0": _("Tag"),
        "url": _("URL"),
    }


class InstitutionPaginator(PageNumberPagination):
    max_page_size = 10000  # increased maximum page size to allow export to CSV without pagination
    page_size_query_param = 'page_size'


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = (
        Institution.objects.select_related("jst")
        .prefetch_related("tags", "parents", "jst", "jst__category")
        .all()
    )
    serializer_class = InstitutionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionFilter
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (InstitutionCSVRenderer,)
    pagination_class = InstitutionPaginator


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
