from atom.ext.django_filters.filters import UserKwargFilterSetMixin
from dal import autocomplete
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import BooleanFilter
from feder.main.filters import MinYearRangeFilter, InitialFilterSet
from .models import Letter
from django.utils.timezone import now


def has_eml(qs, name, value):
    lookup = Q(eml__isnull=True) | Q(eml="")
    return qs.exclude(lookup) if value else qs.filter(lookup)


class LetterFilter(UserKwargFilterSetMixin, InitialFilterSet):
    created = MinYearRangeFilter(label=_("Creation date"))
    eml = BooleanFilter(label=_("Has eml?"), method=has_eml)

    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"created": now().year}
        super().__init__(*args, **kwargs)
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
        fields = ["title", "created", "record__case__institution"]
