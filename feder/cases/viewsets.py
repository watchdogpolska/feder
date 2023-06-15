from io import BytesIO

import openpyxl
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.renderers import BaseRenderer
from rest_framework.settings import api_settings

from feder.main.utils import PaginatedCSVStreamingRenderer

from .filters import CaseReportFilter
from .models import Case
from .serializers import CaseReportSerializer, CaseSerializer


class CaseFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"

    class Meta:
        model = Case
        fields = ["name", "monitoring"]


class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    # TODO missing in tests
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CaseFilter

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class CaseCSVRenderer(PaginatedCSVStreamingRenderer):
    header = CaseReportSerializer.Meta.fields
    labels = {
        "pk": _("Id"),
        "institution_name": _("Name"),
        "institution_email": _("Email of institution"),
        "institution_regon": _("REGON"),
        "teryt": _("Unit of administrative division"),
        "community": _("Community"),
        "county": _("County"),
        "voivodeship": _("Voivodeship"),
        "tags": _("Tags"),
        "first_request_date": _("First request date"),
        "first_request_status": _("First request status"),
        "confirmation_received": _("Confirmation received"),
        "response_received": _("Response received"),
        "last_request_date": _("Last request date"),
        "last_request_status": _("Last request status"),
    }
    results_field = "results"


class CaseExcelRenderer(BaseRenderer):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"
    charset = None
    render_style = "binary"
    labels = CaseCSVRenderer.labels

    def render(self, data, media_type=None, renderer_context=None):
        if data is None:
            return ""
        wb = openpyxl.Workbook()
        sheet = wb.active
        column_keys = [key for key, value in self.labels.items()]
        header = [str(self.labels[col]) for col in column_keys]
        sheet.append(header)
        for row_data_dict in data["results"]:
            row_data = [str(row_data_dict[key]) for key in column_keys]
            sheet.append(row_data)
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return buffer


class CaseReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CaseReportSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CaseReportFilter
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (
        CaseCSVRenderer,
        CaseExcelRenderer,
    )

    # custom attributes:
    file_name_suffix = _("case_report")
    file_name_prefix = ""

    def get_queryset(self):
        qs = (
            Case.objects.prefetch_related("tags")
            .select_related("first_request", "first_request__emaillog")
            .select_related("last_request", "last_request__emaillog")
            .with_institution()
            .for_user(self.request.user)
            .order_by(
                "institution__jst__parent__parent__name",
                "institution__jst__parent__name",
                "institution__jst__name",
                "institution__name",
            )
        )
        if self.request.query_params.get("monitoring"):
            qs = qs.filter(
                monitoring__pk=int(self.request.query_params.get("monitoring"))
            )
            if qs.first():
                self.file_name_prefix = qs.first().monitoring.slug
        return qs

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(self.request.accepted_renderer, CaseCSVRenderer):
            response["Content-Disposition"] = "attachment; filename={}_{}.csv".format(
                self.file_name_prefix, self.file_name_suffix
            )
        elif isinstance(self.request.accepted_renderer, CaseExcelRenderer):
            response["Content-Disposition"] = "attachment; filename={}_{}.xlsx".format(
                self.file_name_prefix, self.file_name_suffix
            )
        return response
