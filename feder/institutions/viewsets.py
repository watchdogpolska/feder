import django_filters
from rest_framework import filters, viewsets
from teryt_tree.rest_framework_ext.viewsets import custom_area_filter

from .models import Institution, Tag
from .serializers import InstitutionSerializer, TagSerializer


class InstitutionFilter(filters.FilterSet):
    jst = django_filters.CharFilter(method=custom_area_filter)

    class Meta:
        model = Institution
        fields = ['tags', 'jst']


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = (Institution.objects.
                select_related('jst').
                prefetch_related('tags').
                all())
    serializer_class = InstitutionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
