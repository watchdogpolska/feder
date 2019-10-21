import django_filters
from django_filters import rest_framework as filters
from rest_framework import viewsets

from .models import Record
from .serializers import RecordSerializer


class RecordFilter(filters.FilterSet):
    case = django_filters.CharFilter()
    o = django_filters.OrderingFilter(
        fields=["created", "-created", "modified", "-modified"]
    )

    class Meta:
        model = Record
        fields = ["case"]


class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Record.objects.for_api().select_related().all()
    serializer_class = RecordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RecordFilter
