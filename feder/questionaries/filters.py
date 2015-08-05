# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter
import django_filters
from .models import Questionary


class QuestionaryFilter(CrispyFilterMixin, django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_type='icontains')
    # institution = AutocompleteChoiceFilter('InstitutionAutocomplete')
    form_class = None

    def __init__(self, *args, **kwargs):
        super(QuestionaryFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Questionary
        # fields = ['name', 'monitoring', 'institution']
        # order_by = ['-letter_count', 'created', ]
