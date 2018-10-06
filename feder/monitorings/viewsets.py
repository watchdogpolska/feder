import django_filters
try:
    from django_filters import rest_framework as filters
except ImportError:  # Back-ward compatible for django-rest-framework<3.7
    from rest_framework import filters
from rest_framework import viewsets

from .models import Monitoring
from .serializers import MonitoringSerializer


class MonitoringViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filter_class = RecordFilter
