# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r'^case-(?P<case_pk>[\d-]+)$'), views.EmailLogCaseListView.as_view(),
        name="list"),
    url(_(r'^monitoring-(?P<monitoring_pk>[\d-]+)$'), views.EmailLogMonitoringListView.as_view(),
        name="list"),
    url(_(r'^monitoring-(?P<monitoring_pk>[\d-]+)/export$'), views.EmailLogMonitoringCsvView.as_view(),
        name="export"),
    url(_(r'^log-(?P<pk>[\d-]+)$'), views.EmailLogDetailView.as_view(),
        name="detail"),
]
