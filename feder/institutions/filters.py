import django_filters
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from teryt_tree.dal_ext.filters import VoivodeshipFilter, CountyFilter, CommunityFilter

from .models import Institution


class InstitutionFilter(django_filters.FilterSet):
    voivodeship = VoivodeshipFilter(
        widget=autocomplete.ModelSelect2(url='teryt:voivodeship-autocomplete')
    )
    county = CountyFilter(
        widget=autocomplete.ModelSelect2(url='teryt:county-autocomplete',
                                         forward=['voivodeship'])
    )
    community = CommunityFilter(
        widget=autocomplete.ModelSelect2(url='teryt:community-autocomplete',
                                         forward=['county'])
    )

    def __init__(self, *args, **kwargs):
        super(InstitutionFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'
        widget = autocomplete.Select2Multiple(url='institutions:tag_autocomplete')
        self.filters['tags'].widget = widget

    class Meta:
        model = Institution
        fields = ['name', 'tags']
        order_by = [
            ('case_count', _('Cases count (descending)')),
            ('-case_count', _('Cases count (ascending)')),
            ('jst', _('Area')),
        ]
