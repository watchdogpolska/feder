from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.settings import api_settings

from .models import Case
from .serializers import CaseSerializer, CaseReportSerializer
from feder.main.utils import PaginatedCSVStreamingRenderer
from feder.main.mixins import CsvRendererViewMixin


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


class CaseReportFilter(filters.FilterSet):
    class Meta:
        model = Case
        fields = ["name", "monitoring"]


class CaseCSVRenderer(PaginatedCSVStreamingRenderer):
    header = CaseReportSerializer.Meta.fields
    labels = {
        "pk": _("Id"),
        "institution_name": _("Name"),
        "institution_email": _("Email of institution"),
        "community": _("REGON number"),
        "county": _("County"),
        "voivodeship": _("Voivodeship"),
        "request_date": _("Request date"),
        "request_status": _("Request status"),
        "response_received": _("Response received"),
        "receiving_confirmed": _("Receiving confirmed"),
    }
    results_field = "results"


class CaseReportViewSet(CsvRendererViewMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = CaseReportSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CaseReportFilter
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CaseCSVRenderer,)

    # custom attributes:
    csv_file_name = _("case_report")

    def get_queryset(self):
        return Case.objects.select_related(
            "institution",
            "institution__jst",
            "institution__jst__parent",
            "institution__jst__parent__parent",
        )
