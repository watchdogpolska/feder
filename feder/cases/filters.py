# -*- coding: utf-8 -*-
import django_filters
from django.utils.translation import ugettext_lazy as _
from dal import autocomplete

from .models import Case


class CaseFilter(django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))

    def __init__(self, *args, **kwargs):
        super(CaseFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_expr = 'icontains'
        self.filters['monitoring'].widget = autocomplete.ModelSelect2(
            url='monitorings:autocomplete')
        self.filters['institution'].widget = autocomplete.ModelSelect2(
            url='institutions:autocomplete')

    class Meta:
        model = Case
        fields = ['name', 'monitoring', 'institution', 'created']
        order_by = [
            ('letter_count', _('Letter count (descending)')),
            ('-letter count', _('Letter count (ascending)')),
            ('created', _('creation date (ascending)')),
            ('-created', _('creation date (descending)')),
        ]
