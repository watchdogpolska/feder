# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^monitoring-(?P<monitoring>[\d]+)$', views.AlertListView.as_view(),
        name="list"),
    url(r'^monitoring-(?P<monitoring>[\d]+)/~create$', views.AlertCreateView.as_view(),
        name="create"),
    url(r'^alert-(?P<pk>[\d]+)$', views.AlertDetailView.as_view(),
        name="details"),
    url(r'^alert-(?P<pk>[\d]+)/~update$', views.AlertUpdateView.as_view(),
        name="update"),
    url(r'^alert-(?P<pk>[\d]+)/~delete$', views.AlertDeleteView.as_view(),
        name="delete"),
    url(r'^alert-(?P<pk>[\d]+)/~status$', views.AlertStatusView.as_view(),
        name="status"),
]
