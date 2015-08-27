# -*- coding: utf-8 -*-
import django_filters
from django.utils.translation import ugettext_lazy as _

from atom.filters import AutocompleteChoiceFilter, CrispyFilterMixin

from .models import Task


class TaskFilter(CrispyFilterMixin, django_filters.FilterSet):
    case = AutocompleteChoiceFilter('CaseAutocomplete')
    questionary = AutocompleteChoiceFilter('QuestionaryAutocomplete')
    case__institution = AutocompleteChoiceFilter('InstitutionAutocomplete')
    case__monitoring = AutocompleteChoiceFilter('MonitoringAutocomplete')
    created = django_filters.DateRangeFilter(label=_("Creation date"))
    done = django_filters.BooleanFilter(label=_("Is done?"),
                                        action=lambda qs, v: qs.is_done(exclude=not v))
    form_class = None

    def __init__(self, *args, **kwargs):
        super(TaskFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'

    class Meta:
        model = Task
        fields = ['name', 'case', 'questionary', 'case__institution', ]
        order_by = [
                    ('created', _('creation date (ascending)')),
                    ('-created', _('creation date (descending)')),
            ]
