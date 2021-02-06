import django_filters
from dal import autocomplete
from django.db.models import Q
from django import forms
from django.utils.translation import ugettext_lazy as _
from teryt_tree.dal_ext.filters import VoivodeshipFilter, CountyFilter, CommunityFilter

from .models import Monitoring
from feder.teryt.filters import (
    DisabledWhenVoivodeshipFilter,
    DisabledWhenCountyFilter,
    DisabledWhenCommunityFilter,
)
from feder.cases.models import Case
from feder.cases_tags.models import Tag


class MonitoringFilter(django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))
    voivodeship = DisabledWhenVoivodeshipFilter()
    county = DisabledWhenCountyFilter()
    community = DisabledWhenCommunityFilter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"
        self.filters["name"].label = _("Name")

    class Meta:
        model = Monitoring
        fields = ["name", "created"]


class ReportMonitoringFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        label=_("institution name"),
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
        label=_("tags"), field_name="tags", widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        case = kwargs["queryset"].first()
        self.filters["tags"].queryset = (
            Tag.objects.filter(
                Q(monitoring__isnull=True) | Q(monitoring=case.monitoring)
            )
            if case
            else Tag.objects.none()
        )

    class Meta:
        model = Case
        fields = []
