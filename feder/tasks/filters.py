# -*- coding: utf-8 -*-
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter
import django_filters
from .models import Task


class TaskFilter(CrispyFilterMixin, django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_type='icontains')
    # institution = AutocompleteChoiceFilter('InstitutionAutocomplete')
    # monitoring = AutocompleteChoiceFilter('MonitoringAutocomplete')

    form_class = None

    def __init__(self, *args, **kwargs):
        super(TaskFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Task
        # fields = ['name', 'monitoring', 'institution']
        # order_by = ['-letter_count', 'created', ]
