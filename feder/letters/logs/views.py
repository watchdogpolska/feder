# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from braces.views import SelectRelatedMixin, PrefetchRelatedMixin
from cached_property import cached_property
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from feder.cases.models import Case
from feder.letters.logs.models import EmailLog
from feder.main.mixins import AttrPermissionRequiredMixin
from feder.monitorings.models import Monitoring


class ListMonitoringMixin(AttrPermissionRequiredMixin, SelectRelatedMixin):
    select_related = ['case']

    def get_permission_object(self):
        return self.monitoring

    def get_queryset(self):
        return super(ListMonitoringMixin, self).get_queryset().filter(case__monitoring=self.monitoring)

    def get_context_data(self, **kwargs):
        kwargs['monitoring'] = self.monitoring
        return super(ListMonitoringMixin, self).get_context_data(**kwargs)


class EmailLogMonitoringListView(ListMonitoringMixin, ListView):
    template_name_suffix = '_list_for_monitoring'
    model = EmailLog
    permission_required = 'monitorings.view_log'
    paginate_by = 100

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, pk=self.kwargs['monitoring_pk'])


class EmailLogCaseListView(ListMonitoringMixin, ListView):
    template_name_suffix = '_list_for_case'
    model = EmailLog
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.view_log'

    @cached_property
    def case(self):
        return get_object_or_404(Case.objects.select_related('monitoring'),
                                 pk=self.kwargs['case_pk'])

    @cached_property
    def monitoring(self):
        return self.case.monitoring

    def get_permission_object(self):
        return self.monitoring

    def get_context_data(self, **kwargs):
        kwargs['case'] = self.case
        return super(EmailLogCaseListView, self).get_context_data(**kwargs)

    def get_queryset(self):
        return super(ListMonitoringMixin, self).get_queryset().filter(case=self.case)


class EmailLogDetailView(AttrPermissionRequiredMixin, PrefetchRelatedMixin,
                         SelectRelatedMixin, DetailView):
    model = EmailLog
    select_related = ['case__monitoring']
    prefetch_related = ['logrecord_set']
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.view_log'
