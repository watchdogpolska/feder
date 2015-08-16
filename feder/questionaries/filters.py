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

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(QuestionaryFilter, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            del self.filters['lock']

    class Meta:
        model = Questionary
        fields = ['title', 'monitoring', 'created', 'lock']
        order_by = ['created', ]
