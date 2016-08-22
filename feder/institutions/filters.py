import django_filters
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from django_filters.filters import ModelChoiceFilter
from teryt_tree.filters import JSTModelChoice

from .models import Institution, Tag


class InstitutionFilter(django_filters.FilterSet):
    voivodeship = JSTModelChoice(level=1, label=_("Voivodeship"))
    county = JSTModelChoice(level=2, label=_("County"))
    community = JSTModelChoice(level=3, label=_("Community"))
    tags = ModelChoiceFilter(
        label=_("Tags"),
        required=False,
        queryset=Tag.objects.all(),
        widget=autocomplete.ModelSelect2(url='institutions:tag_autocomplete'),
    )

    def __init__(self, *args, **kwargs):
        super(InstitutionFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'
        if self.data.get('voivodeship', None):
            self.filters['county'].limit_parent(self.data.get('voivodeship'))
            if self.data.get('county', None):
                self.filters['community'].limit_parent(self.data.get('county'))
            else:
                del self.filters['community']
        else:
            del self.filters['county']
            del self.filters['community']

    class Meta:
        model = Institution
        fields = ['name', 'tags']
        order_by = [
            ('case_count', _('Cases count (descending)')),
            ('-case_count', _('Cases count (ascending)')),
            ('jst', _('Area')),
        ]
