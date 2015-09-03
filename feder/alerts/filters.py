# -*- coding: utf-8 -*-
import django_filters
from atom.filters import AutocompleteChoiceFilter, CrispyFilterMixin
from django.utils.translation import ugettext_lazy as _

from .models import Alert


class AlertFilter(CrispyFilterMixin, django_filters.FilterSet):

    author = AutocompleteChoiceFilter('UserAutocomplete', label=_("Author"))
    form_class = None

    def __init__(self, *args, **kwargs):
        super(AlertFilter, self).__init__(*args, **kwargs)
        self.filters['reason'].lookup_type = 'icontains'

    class Meta:
        model = Alert
        fields = ['reason', 'author', 'status']
