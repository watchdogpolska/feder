# -*- coding: utf-8 -*-
from atom.filters import CrispyFilterMixin
import django_filters
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import Monitoring


class MonitoringFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None
    created = django_filters.DateRangeFilter(label=_("Creation date"))

    def __init__(self, *args, **kwargs):
        super(MonitoringFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'
        self.filters['user'].extra['queryset'] = (get_user_model().objects.
            annotate(case_count=Count('case')).filter(case_count__gt=0).all())

    class Meta:
        model = Monitoring
        fields = ['name', 'user', 'created']
        order_by = ['created', '-created', 'case_count']
