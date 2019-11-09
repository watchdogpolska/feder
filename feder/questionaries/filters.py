from atom.ext.django_filters.filters import UserKwargFilterSetMixin
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter, DateRangeFilter, FilterSet

from .models import Questionary


class QuestionaryFilter(UserKwargFilterSetMixin, FilterSet):
    title = CharFilter(lookup_expr="icontains", label=_("Name"))
    created = DateRangeFilter(label=_("Creation date"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.user.is_superuser:
            del self.filters["lock"]
        self.filters["monitoring"].widget = autocomplete.ModelSelect2(
            url="monitorings:autocomplete"
        )

    class Meta:
        model = Questionary
        fields = ["title", "monitoring", "created", "lock"]
        order_by = [
            ("created", _("Creation date (ascending)")),
            ("-created", _("Creation date (descending)")),
        ]
