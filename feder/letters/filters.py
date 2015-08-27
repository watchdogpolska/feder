# -*- coding: utf-8 -*-
import django_filters
from atom.filters import AutocompleteChoiceFilter, CrispyFilterMixin
from django.utils.translation import ugettext_lazy as _

from .models import Letter


class LetterFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None
    institution = AutocompleteChoiceFilter('InstitutionAutocomplete',
                                           name='case__institution')
    created = django_filters.DateRangeFilter(label=_("Creation date"))

    def __init__(self, *args, **kwargs):
        super(LetterFilter, self).__init__(*args, **kwargs)
        self.filters['title'].lookup_type = 'icontains'

    class Meta:
        model = Letter
        order_by = [
            ('created', _('Creation date (ascending)')),
            ('-created', _('Creation date (descending)')),
        ]
        fields = ['title', 'created']
