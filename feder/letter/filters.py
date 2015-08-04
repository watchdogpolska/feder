# -*- coding: utf-8 -*-
from .models import Letter
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter
import django_filters


class LetterFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None
    name = django_filters.CharFilter(lookup_type='icontains')
    institution = AutocompleteChoiceFilter('InstitutionAutocomplete', name='case__institution')

    def __init__(self, *args, **kwargs):
        super(LetterFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Letter
        order_by = ['title', 'created']
        fields = ['name', ]
