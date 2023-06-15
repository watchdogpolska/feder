import django_filters
from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _
from teryt_tree.dal_ext.filters import CommunityFilter, CountyFilter, VoivodeshipFilter

from feder.cases_tags.models import Tag
from feder.letters.logs.models import STATUS as EMAIL_LOG_STATUS
from feder.main.filters import InitialFilterSet, MinYearRangeFilter
from feder.main.mixins import DisabledWhenFilterSetMixin
from feder.monitorings.models import Monitoring
from feder.teryt.filters import (
    DisabledWhenCommunityFilter,
    DisabledWhenCountyFilter,
    DisabledWhenVoivodeshipFilter,
)

from .models import Case


class CaseFilter(DisabledWhenFilterSetMixin, InitialFilterSet):
    created = MinYearRangeFilter(label=_("Creation date"))
    voivodeship = DisabledWhenVoivodeshipFilter()
    county = DisabledWhenCountyFilter()
    community = DisabledWhenCommunityFilter()

    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"created": "year"}
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"
        self.filters["name"].label = _("Name")
        self.filters["monitoring"].field.widget = autocomplete.ModelSelect2(
            url="monitorings:autocomplete"
        )
        self.filters["institution"].field.widget = autocomplete.ModelSelect2(
            url="institutions:autocomplete"
        )

    class Meta:
        model = Case
        fields = [
            "name",
            "monitoring",
            "institution",
            "created",
            "confirmation_received",
            "response_received",
        ]


class CaseReportFilter(django_filters.FilterSet):
    monitoring = django_filters.ModelChoiceFilter(queryset=Monitoring.objects.all())
    name = django_filters.CharFilter(
        label=_("Institution name"),
        field_name="institution__name",
        lookup_expr="icontains",
    )
    voivodeship = VoivodeshipFilter(
        widget=autocomplete.ModelSelect2(url="teryt:voivodeship-autocomplete")
    )
    county = CountyFilter(
        widget=autocomplete.ModelSelect2(
            url="teryt:county-autocomplete", forward=["voivodeship"]
        )
    )
    community = CommunityFilter(
        widget=autocomplete.ModelSelect2(
            url="teryt:community-autocomplete", forward=["county"]
        )
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        label=_("Tags"), field_name="tags", widget=forms.CheckboxSelectMultiple
    )
    first_request_date = django_filters.DateFromToRangeFilter(
        label=_("First request date"), field_name="first_request__created"
    )
    first_request_status = django_filters.ChoiceFilter(
        label=_("First request status"),
        field_name="first_request__emaillog__status",
        choices=EMAIL_LOG_STATUS,
    )
    last_request_date = django_filters.DateFromToRangeFilter(
        label=_("Last request date"), field_name="last_request__created"
    )
    last_request_status = django_filters.ChoiceFilter(
        label=_("Last request status"),
        field_name="last_request__emaillog__status",
        choices=EMAIL_LOG_STATUS,
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        case = queryset.first()
        self.filters["tags"].queryset = (
            Tag.objects.for_monitoring(case.monitoring) if case else Tag.objects.none()
        )

    class Meta:
        model = Case
        fields = [
            "monitoring",
            "name",
            "voivodeship",
            "county",
            "community",
            "tags",
            "first_request_date",
            "first_request_status",
            "last_request_date",
            "last_request_status",
            "confirmation_received",
            "response_received",
        ]
