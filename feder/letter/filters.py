# -*- coding: utf-8 -*-
from .models import Letter
from atom.filters import CrispyFilterMixin
import django_filters


class LetterFilter(CrispyFilterMixin, django_filters.FilterSet):
    form_class = None

    def __init__(self, *args, **kwargs):
        super(LetterFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Letter
        # order_by = ['', ]
