# -*- coding: utf-8 -*-
import django_filters
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.db.models import Count
from django import forms
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django_filters import STRICTNESS

from .models import Monitoring
from teryt_tree.dal_ext.filters import VoivodeshipFilter, CountyFilter, CommunityFilter


class DisabledWhenMixin(object):
    def __init__(self, *args, **kwargs):
        self.disabled_when = kwargs.pop('disabled_when', [])
        super(DisabledWhenMixin, self).__init__(*args, **kwargs)


class DisabledWhenVoivodeshipFilter(DisabledWhenMixin, VoivodeshipFilter):
    pass


class DisabledWhenCountyFilter(DisabledWhenMixin, CountyFilter):
    pass


class DisabledWhenCommunityFilter(DisabledWhenMixin, CommunityFilter):
    pass


class MonitoringFilter(django_filters.FilterSet):
    created = django_filters.DateRangeFilter(label=_("Creation date"))
    voivodeship = DisabledWhenVoivodeshipFilter(
        widget=autocomplete.ModelSelect2(url='teryt:voivodeship-autocomplete'),
        disabled_when=['county', 'voivodeship']
    )
    county = DisabledWhenCountyFilter(
        widget=autocomplete.ModelSelect2(url='teryt:county-autocomplete',
                                         forward=['voivodeship']),
        disabled_when=['community']

    )
    community = DisabledWhenCommunityFilter(
        widget=autocomplete.ModelSelect2(url='teryt:community-autocomplete',
                                         forward=['county']),
        disabled_when=[]
    )

    def check_enabled_filter(self, filter, form):
        if not getattr(filter, 'disabled_when', None):
            return True
        return all(form.cleaned_data[field] for field in filter.disabled_when)

    @property
    def qs(self):
        # Source: django_filters/filters.py
        if not hasattr(self, '_qs'):
            if not self.is_bound:
                self._qs = self.queryset.all()
                return self._qs

            if not self.form.is_valid():
                if self.strict == STRICTNESS.RAISE_VALIDATION_ERROR:
                    raise forms.ValidationError(self.form.errors)
                elif self.strict == STRICTNESS.RETURN_NO_RESULTS:
                    self._qs = self.queryset.none()
                    return self._qs

            qs = self.queryset.all()
            for name, filter_ in six.iteritems(self.filters):
                value = self.form.cleaned_data.get(name)
                if value is not None and self.check_enabled_filter(filter_, self.form):  # valid & clean data
                    qs = filter_.filter(qs, value)

            self._qs = qs

        return self._qs

    def __init__(self, *args, **kwargs):
        super(MonitoringFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_expr = 'icontains'
        self.filters['name'].label = _("Name")
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
