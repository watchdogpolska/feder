from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.settings import api_settings

from .filters import CaseReportFilter
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

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class CaseCSVRenderer(PaginatedCSVStreamingRenderer):
    header = CaseReportSerializer.Meta.fields
    labels = {
        "pk": _("Id"),
        "institution_name": _("Name"),
        "institution_email": _("Email of institution"),
        "institution_regon": _("REGON"),
        "community": _("Community"),
        "county": _("County"),
        "voivodeship": _("Voivodeship"),
        "tags": _("Tags"),
        "request_date": _("Request date"),
        "request_status": _("Request status"),
        "confirmation_received": _("Confirmation received"),
        "response_received": _("Response received"),
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
        return (
            Case.objects.with_institution()
            .with_application_letter_date()
            .with_application_letter_status()
            .for_user(self.request.user)
            .order_by(
                "institution__jst__parent__parent__name",
                "institution__jst__parent__name",
                "institution__jst__name",
                "institution__name",
            )
        )
