# -*- coding: utf-8 -*-
from atom.ext.django_filters.filters import (
    AutocompleteChoiceFilter,
    CrispyFilterMixin,
    UserKwargFilterSetMixin
)
from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter, DateRangeFilter, FilterSet

from .models import Questionary


class QuestionaryFilter(UserKwargFilterSetMixin, CrispyFilterMixin, FilterSet):
    title = CharFilter(lookup_type='icontains', label=_("Name"))
    monitoring = AutocompleteChoiceFilter('MonitoringAutocomplete', label=_("Monitoring"))
    created = DateRangeFilter(label=_("Creation date"))
    form_class = None

    def __init__(self, *args, **kwargs):
        super(QuestionaryFilter, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            del self.filters['lock']

    class Meta:
        model = Questionary
        fields = ['title', 'monitoring', 'created', 'lock']
        order_by = [
            ('created', _('Creation date (ascending)')),
            ('-created', _('Creation date (descending)')),
        ]
