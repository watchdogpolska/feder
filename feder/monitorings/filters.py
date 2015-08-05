# -*- coding: utf-8 -*-
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter
import django_filters
from .models import Monitoring


class MonitoringFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None
    name = django_filters.CharFilter(lookup_type='icontains')
    user = AutocompleteChoiceFilter('UserAutocomplete')

    def __init__(self, *args, **kwargs):
        super(MonitoringFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Monitoring
        fields = ['name', 'user']
        order_by = ['created', '-created']
