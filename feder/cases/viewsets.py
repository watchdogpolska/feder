import django_filters
from django_filters import rest_framework as filters
from rest_framework import viewsets

from .models import Case
from .serializers import CaseSerializer


class CaseFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"

    class Meta:
        model = Case
        fields = ["name", "monitoring"]


class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CaseFilter
