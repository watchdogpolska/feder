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


# TODO tests are missing !!!!!!!!


class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecordFilter
    queryset = Record.objects.for_api().select_related().all()

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)
