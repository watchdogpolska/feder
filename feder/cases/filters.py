import django_filters
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _

from .models import Case
from feder.main.mixins import DisabledWhenFilterSetMixin
from feder.teryt.filters import (
    DisabledWhenVoivodeshipFilter,
    DisabledWhenCountyFilter,
    DisabledWhenCommunityFilter,
)


class CaseFilter(DisabledWhenFilterSetMixin, django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))
    voivodeship = DisabledWhenVoivodeshipFilter()
    county = DisabledWhenCountyFilter()
    community = DisabledWhenCommunityFilter()

    def __init__(self, *args, **kwargs):
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
        fields = ["name", "monitoring", "institution", "created"]
