# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
import django_filters
from .models import Questionary
from atom.filters import CrispyFilterMixin, AutocompleteChoiceFilter


class QuestionaryFilter(CrispyFilterMixin, django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_type='icontains', label=_("Name"))
    monitoring = AutocompleteChoiceFilter('MonitoringAutocomplete', label=_("Monitoring"))
    created = django_filters.DateRangeFilter(label=_("Creation date"))
    form_class = None

    def __init__(self, *args, **kwargs):
        super(QuestionaryFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Questionary
        fields = ['title', 'monitoring', 'created']
        order_by = ['created', ]
