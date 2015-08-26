# -*- coding: utf-8 -*-
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter
from django.utils.translation import ugettext_lazy as _
import django_filters
from .models import Case


class CaseFilter(CrispyFilterMixin, django_filters.FilterSet):
    institution = AutocompleteChoiceFilter('InstitutionAutocomplete', label=_("Institution"))
    monitoring = AutocompleteChoiceFilter('MonitoringAutocomplete', label=_("Monitoring"))
    created = django_filters.DateRangeFilter(label=_("Creation date"))

    form_class = None

    def __init__(self, *args, **kwargs):
        super(CaseFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'

    class Meta:
        model = Case
        fields = ['name', 'monitoring', 'institution', 'created']
        order_by = [
                    ('letter_count', _('Letter count (descending)')),
                    ('-letter count', _('Letter count (ascending)')),
                    ('created', _('creation date (ascending)')),
                    ('-created', _('creation date (descending)')),
            ]
