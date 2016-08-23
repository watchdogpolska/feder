# -*- coding: utf-8 -*-
import django_filters
from dal import autocomplete
from .models import Alert


class AlertFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(AlertFilter, self).__init__(*args, **kwargs)
        self.filters['reason'].lookup_type = 'icontains'
        self.filters['user'].widget = autocomplete.ModelSelect2(url='users:autocomplete')

    class Meta:
        model = Alert
        fields = ['reason', 'author', 'status']
