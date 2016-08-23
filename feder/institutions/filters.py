import django_filters
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from teryt_tree.filters import JSTModelChoice

from .models import Institution


class InstitutionFilter(django_filters.FilterSet):
    voivodeship = JSTModelChoice(level=1, label=_("Voivodeship"))
    county = JSTModelChoice(level=2, label=_("County"))
    community = JSTModelChoice(level=3, label=_("Community"))

    def __init__(self, *args, **kwargs):
        super(InstitutionFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'
        self.filters['tags'].widget = autocomplete.ModelSelect2(url='institutions:tag_autocomplete')

    class Meta:
        model = Institution
        fields = ['name', 'tags']
        order_by = [
            ('case_count', _('Cases count (descending)')),
            ('-case_count', _('Cases count (ascending)')),
            ('jst', _('Area')),
        ]
