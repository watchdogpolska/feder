import django_filters
from dal import autocomplete
from django.utils.translation import gettext_lazy as _
from teryt_tree.dal_ext.filters import VoivodeshipFilter, CountyFilter, CommunityFilter

from .models import Institution


class InstitutionFilter(django_filters.FilterSet):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].lookup_expr = "icontains"
        self.filters["name"].label = _("Name")
        widget = autocomplete.Select2Multiple(url="institutions:tag_autocomplete")
        # TODO: Verify below on django-filter 2.2.0
        self.filters["tags"].field.widget = widget

    class Meta:
        model = Institution
        fields = ["name", "tags", "regon"]
