# -*- coding: utf-8 -*-
from .models import Letter
from django.utils.translation import ugettext_lazy as _
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter
import django_filters


class LetterFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None
    title = django_filters.CharFilter(lookup_type='icontains', label=_("Title"))
    institution = AutocompleteChoiceFilter('InstitutionAutocomplete',
        name='case__institution', label=_("Institution"))
    created = django_filters.DateRangeFilter(label=_("Creation date"))

    def __init__(self, *args, **kwargs):
        super(LetterFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Letter
        order_by = ['created', ]
        fields = ['title', 'created']
