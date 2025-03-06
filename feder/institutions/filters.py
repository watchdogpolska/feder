import django_filters
from dal import autocomplete
from django.forms import Select
from django.utils.translation import gettext_lazy as _
from teryt_tree.dal_ext.filters import CommunityFilter, CountyFilter, VoivodeshipFilter

from .models import Institution


class InstitutionFilter(django_filters.FilterSet):
    TAGS_MODE_CHOICES = [
        ("AND", "AND"),
        ("OR", "OR"),
    ]
    tags_mode = django_filters.filters.ChoiceFilter(
        choices=TAGS_MODE_CHOICES,
        widget=Select(),
        method="filter_tags",
        label=_("Tags filter mode"),
        initial="OR",
        empty_label=None,
    )
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
        # TODO: Verify below on django-filter 2.2.0
        self.filters["tags"].field.widget = autocomplete.Select2Multiple(
            url="institutions:tag_autocomplete"
        )

    def filter_tags(self, queryset, name, value):
        if value == "AND" and self.form.cleaned_data["tags"]:
            for tag in self.form.cleaned_data["tags"]:
                queryset = queryset.filter(tags__name=tag)
        elif value == "OR" and self.form.cleaned_data["tags"]:
            queryset = queryset.filter(tags__name__in=self.form.cleaned_data["tags"])
        return queryset

    class Meta:
        model = Institution
        fields = ["name", "regon", "tags", "archival", "jst__active"]
