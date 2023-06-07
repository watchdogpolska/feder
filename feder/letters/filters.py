from atom.ext.django_filters.filters import UserKwargFilterSetMixin
from dal import autocomplete
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter

from feder.main.filters import InitialFilterSet, MinYearRangeFilter

from .models import Letter


def has_eml(qs, name, value):
    if value is None:
        return qs
    lookup = Q(eml__isnull=True)
    return qs.exclude(lookup) if value else qs.filter(lookup)


class LetterFilter(UserKwargFilterSetMixin, InitialFilterSet):
    created = MinYearRangeFilter(label=_("Creation date"))
    has_eml = BooleanFilter(label=_("Has eml?"), method=has_eml)

    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"created": "year"}
        super().__init__(*args, **kwargs)
        self.filters["title"].lookup_expr = "icontains"
        self.filters["title"].label = _("Title")
        self.filters[
            "record__case__institution"
        ].field.widget = autocomplete.ModelSelect2(url="institutions:autocomplete")
        self.filters["record__case__institution"].label = _("Institution")
        if not self.user.has_perm("letters.can_filter_eml"):
            del self.filters["has_eml"]

    class Meta:
        model = Letter
        fields = ["title", "created", "record__case__institution"]
