import django_filters
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _

from .models import Case


class CaseFilter(django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))

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
        order_by = [
            ("record_count", _("Record count (descending)")),
            ("-record_count", _("Record count (ascending)")),
            ("created", _("creation date (ascending)")),
            ("-created", _("creation date (descending)")),
        ]
