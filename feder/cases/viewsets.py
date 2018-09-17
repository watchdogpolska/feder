import django_filters
try:
    from django_filters import rest_framework as filters
except ImportError:  # Back-ward compatible for django-rest-framework<3.7
    from rest_framework import filters
from rest_framework import viewsets

from .models import Case
from .serializers import CaseSerializer


class CaseFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(CaseFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_expr = 'icontains'

    class Meta:
        model = Case
        fields = ['name', 'monitoring']


class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CaseFilter
