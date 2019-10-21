# -*- coding: utf-8 -*-
from atom.ext.django_filters.filters import UserKwargFilterSetMixin
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from django_filters import BooleanFilter, DateRangeFilter, FilterSet

from .models import Letter


def has_eml(qs, v):
    return qs.filter(eml="") if v else qs.exclude(eml="")


class LetterFilter(UserKwargFilterSetMixin, FilterSet):
    created = DateRangeFilter(label=_("Creation date"))
    eml = BooleanFilter(label=_("Has eml?"), method=has_eml)

    def __init__(self, *args, **kwargs):
        super(LetterFilter, self).__init__(*args, **kwargs)
        self.filters["title"].lookup_expr = "icontains"
        self.filters["title"].label = _("Title")
        self.filters[
            "record__case__institution"
        ].field.widget = autocomplete.ModelSelect2(url="institutions:autocomplete")
        self.filters["record__case__institution"].label = _("Institution")
        if not self.user.has_perm("letters.can_filter_eml"):
            del self.filters["eml"]

    class Meta:
        model = Letter
        order_by = [
            ("created", _("Creation date (ascending)")),
            ("-created", _("Creation date (descending)")),
        ]
        fields = ["title", "created", "record__case__institution"]
