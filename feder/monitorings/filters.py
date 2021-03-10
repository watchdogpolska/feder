import django_filters
from django.utils.translation import ugettext_lazy as _

from .models import Monitoring
from feder.teryt.filters import (
    DisabledWhenVoivodeshipFilter,
    DisabledWhenCountyFilter,
    DisabledWhenCommunityFilter,
)
from feder.cases.filters import CaseReportFilter


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


class MonitoringCaseReportFilter(CaseReportFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.filters["monitoring"]

    class Meta(CaseReportFilter.Meta):
        fields = [el for el in CaseReportFilter.Meta.fields if el != "monitoring"]
