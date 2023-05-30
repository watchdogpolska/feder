import django_filters
from django.utils.translation import gettext_lazy as _

from feder.cases.filters import CaseReportFilter
from feder.teryt.filters import (
    DisabledWhenCommunityFilter,
    DisabledWhenCountyFilter,
    DisabledWhenVoivodeshipFilter,
)

from .models import Monitoring


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


class MonitoringCaseAreaFilter(MonitoringFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.form.fields["name"]
        del self.form.fields["created"]


class MonitoringCaseReportFilter(CaseReportFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.filters["monitoring"]

    class Meta(CaseReportFilter.Meta):
        fields = [el for el in CaseReportFilter.Meta.fields if el != "monitoring"]
