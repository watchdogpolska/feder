import django_filters
from django_filters import rest_framework as filters
from rest_framework import viewsets
from teryt_tree.rest_framework_ext.viewsets import custom_area_filter

from .models import Institution, Tag
from .serializers import InstitutionSerializer, TagSerializer


class InstitutionFilter(filters.FilterSet):
    jst = django_filters.CharFilter(method=custom_area_filter)

    def __init__(self, *args, **kwargs):
        super(InstitutionFilter, self).__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"

    class Meta:
        model = Institution
        fields = ["name", "tags", "jst", "regon"]


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = (
        Institution.objects.select_related("jst")
        .prefetch_related("tags", "parents")
        .all()
    )
    serializer_class = InstitutionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
