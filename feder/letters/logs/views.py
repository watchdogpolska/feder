# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
import unicodecsv as csv

from braces.views import SelectRelatedMixin, PrefetchRelatedMixin
from cached_property import cached_property
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from feder.cases.models import Case
from feder.letters.logs.models import EmailLog
from feder.main.mixins import AttrPermissionRequiredMixin
from feder.monitorings.models import Monitoring
from django.views.generic.list import ListView

class ListMonitoringMixin(AttrPermissionRequiredMixin, SelectRelatedMixin):
    select_related = ['case']
    paginate_by = 100
    model = EmailLog
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.view_log'

    def get_permission_object(self):
        return self.monitoring

    def get_queryset(self):
        return super(ListMonitoringMixin, self).get_queryset().filter(case__monitoring=self.monitoring).with_logrecord_count()

    def get_context_data(self, **kwargs):
        kwargs['monitoring'] = self.monitoring
        return super(ListMonitoringMixin, self).get_context_data(**kwargs)


class EmailLogMonitoringListView(ListMonitoringMixin, ListView):
    template_name_suffix = '_list_for_monitoring'
    permission_required = 'monitorings.view_log'

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, pk=self.kwargs['monitoring_pk'])


class EmailLogMonitoringCsvView(ListMonitoringMixin, ListView):
    permission_required = 'monitorings.view_log'

    select_related = ['case', 'case__institution']

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, pk=self.kwargs['monitoring_pk'])

    def get(self, *args, **kwargs):
        response = self._get_csv_response()
        self._write_rows(response, self.get_queryset())
        return response

    @staticmethod
    def _get_base_model_field_names(queryset):
        opts = queryset.model._meta
        return [field.name for field in opts.fields if field.related_model is None]

    def _get_csv_response(self):
        csv_response = HttpResponse(content_type='text/csv')
        current_time = timezone.now()
        filename = 'email_log_{0}-{1}-{2}.csv'.format(self.monitoring.id,
                                                      current_time.strftime('%Y_%m_%d-%H_%M_%S'),
                                                      current_time.tzname()
                                                      )
        csv_response['Content-Disposition'] = "attachment;filename={0}".format(filename)
        return csv_response

    def _write_rows(self, response, queryset):
        writer = csv.writer(response)

        # automatically add all fields from base table/model
        base_field_names = self._get_base_model_field_names(queryset)

        # print header row
        writer.writerow(base_field_names +
                        [
                            'case id',
                            'case email',
                            'institution',
                            'institution id',
                            'monitoring id']
                        )

        for obj in queryset:
            writer.writerow(
                [getattr(obj, field) for field in base_field_names] + [
                obj.case.id,
                obj.case.email,
                obj.case.institution.name,
                obj.case.institution_id,
                obj.case.monitoring_id,
            ])

class EmailLogCaseListView(ListMonitoringMixin, ListView):
    template_name_suffix = '_list_for_case'

    @cached_property
    def case(self):
        return get_object_or_404(Case.objects.select_related('monitoring'),
                                 pk=self.kwargs['case_pk'])

    @cached_property
    def monitoring(self):
        return self.case.monitoring

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
