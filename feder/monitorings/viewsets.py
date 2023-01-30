from rest_framework import viewsets

from .models import Monitoring
from .serializers import MonitoringSerializer


class MonitoringViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    # TODO check why filters are ignored and bring them back
    # filter_backends = (filters.DjangoFilterBackend,)
    # filter_class = RecordFilter

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)
