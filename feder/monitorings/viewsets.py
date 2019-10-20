import django_filters
from django_filters import rest_framework as filters
from rest_framework import viewsets

from .models import Monitoring
from .serializers import MonitoringSerializer


class MonitoringViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filter_class = RecordFilter
