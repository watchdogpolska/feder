# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MonitoringListView.as_view(),
        name="list"),
    url(r'^~create$', views.MonitoringCreateView.as_view(),
        name="create"),
    url(r'^monitoring-(?P<slug>[\w-]+)$', views.MonitoringDetailView.as_view(),
        name="details"),
    url(r'^monitoring-(?P<slug>[\w-]+)/page-(?P<page>[\d]+)$', views.MonitoringDetailView.as_view(),
        name="details"),
    url(r'^monitoring-(?P<slug>[\w-]+)/~update$', views.MonitoringUpdateView.as_view(),
        name="update"),
    url(r'^monitoring-(?P<slug>[\w-]+)/~delete$', views.MonitoringDeleteView.as_view(),
        name="delete"),
    url(r'^monitoring-(?P<slug>[\w-]+)/~permission/~add$', views.PermissionWizard.as_view(),
        name="perm-add"),
    url(r'^monitoring-(?P<slug>[\w-]+)/~permission-(?P<user_pk>[\d]+)$',
        views.MonitoringUpdatePermissionView.as_view(),
        name="perm-update"),
    url(r'^monitoring-(?P<slug>[\w-]+)/~permission$', views.MonitoringPermissionView.as_view(),
        name="perm"),


]
