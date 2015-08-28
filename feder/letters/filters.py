# -*- coding: utf-8 -*-
from atom.ext.django_filters.filters import (
    AutocompleteChoiceFilter,
    CrispyFilterMixin,
    UserKwargFilterSetMixin
)
from django.utils.translation import ugettext_lazy as _
from django_filters import BooleanFilter, DateRangeFilter, FilterSet

from .models import Letter


class LetterFilter(UserKwargFilterSetMixin, CrispyFilterMixin, FilterSet):
    form_class = None
    institution = AutocompleteChoiceFilter('InstitutionAutocomplete',
                                           name='case__institution')
    created = DateRangeFilter(label=_("Creation date"))
    eml = BooleanFilter(label=_("Has eml?"),
                        action=lambda qs, v: qs.filter(eml='') if v else qs.exclude(eml=''))

    def __init__(self, user, *args, **kwargs):
        super(LetterFilter, self).__init__(*args, **kwargs)
        self.filters['title'].lookup_type = 'icontains'

        if not user.has_perm('letters.can_filter_eml'):
            del self.filters['eml']

    class Meta:
        model = Letter
        order_by = [
            ('created', _('Creation date (ascending)')),
            ('-created', _('Creation date (descending)')),
        ]
        fields = ['title', 'created']
