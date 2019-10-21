# -*- coding: utf-8 -*-
import django_filters
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _

from .models import Task


class TaskFilter(django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))
    done = django_filters.BooleanFilter(
        label=_("Is done?"), method=lambda qs, v: qs.is_done(exclude=not v)
    )

    def __init__(self, *args, **kwargs):
        super(TaskFilter, self).__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"
        self.filters["name"].label = _("Name")
        self.filters["case"].widget = autocomplete.ModelSelect2(
            url="cases:autocomplete"
        )
        self.filters["case__monitoring"].widget = autocomplete.ModelSelect2(
            url="monitorings:autocomplete"
        )
        self.filters["case__monitoring"].label = _("Monitoring")
        self.filters["case__institution"].widget = autocomplete.ModelSelect2(
            url="institutions:autocomplete"
        )
        self.filters["case__institution"].label = _("Institution")

    class Meta:
        model = Task
        fields = ["name", "case", "case__institution", "case__monitoring"]
        order_by = [
            ("created", _("creation date (ascending)")),
            ("-created", _("creation date (descending)")),
        ]
