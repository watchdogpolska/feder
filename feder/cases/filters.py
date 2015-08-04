# -*- coding: utf-8 -*-
from .models import Case
from atom.filters import CrispyFilterMixin
import django_filters


class CaseFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None

    def __init__(self, *args, **kwargs):
        super(CaseFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Case
        order_by = ['-letter_count', 'jst']
