# -*- coding: utf-8 -*-
import django_filters
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from .models import Monitoring


class MonitoringFilter(django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))

    def __init__(self, *args, **kwargs):
        super(MonitoringFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_expr = 'icontains'
        self.filters['name'].label = _("name")
        # Limit users select to which have any cases
        qs = (get_user_model().objects.
              annotate(case_count=Count('case')).
              filter(case_count__gt=0).all())
        self.filters['user'].extra['queryset'] = qs
        self.filters['user'].widget = autocomplete.ModelSelect2(url='users:autocomplete')

    class Meta:
        model = Monitoring
        fields = ['name', 'user', 'created']
        order_by = ['created', '-created', '-case_count']
        order_by = [
            ('created', _('Creation date (ascending)')),
            ('-created', _('Creation date (descending)')),
            ('case_count', _('Cases count (ascending)')),
            ('-case_count', _('Cases count (descending)')),
        ]
