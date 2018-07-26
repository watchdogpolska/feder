# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^~create-incoming-(?P<case_pk>\d+)$', views.IncomingParcelPostCreateView.as_view(),
        name="incoming-create"),
    url(r'^incoming-(?P<pk>[\w-]+)$', views.IncomingParcelPostDetailView.as_view(),
        name="incoming-details"),
    url(r'^incoming-(?P<pk>[\w-]+)/~update$', views.IncomingParcelPostUpdateView.as_view(),
        name="incoming-update"),
    url(r'^incoming-(?P<pk>[\w-]+)/~delete$', views.IncomingParcelPostDeleteView.as_view(),
        name="incoming-delete"),
    url(r'^incoming-(?P<pk>[\w-]+)/~download', views.IncomingAttachmentParcelPostXSendFileView.as_view(),
        name="incoming-download"),
    url(r'^~create-outgoing-(?P<case_pk>\d+)$', views.OutgoingParcelPostCreateView.as_view(),
        name="outgoing-create"),
    url(r'^outgoing-(?P<pk>[\w-]+)$', views.OutgoingParcelPostDetailView.as_view(),
        name="outgoing-details"),
    url(r'^outgoing-(?P<pk>[\w-]+)/~update$', views.OutgoingParcelPostUpdateView.as_view(),
        name="outgoing-update"),
    url(r'^outgoing-(?P<pk>[\w-]+)/~delete$', views.OutgoingParcelPostDeleteView.as_view(),
        name="outgoing-delete"),
    url(r'^outgoing-(?P<pk>[\w-]+)/~outgoing', views.OutgoingAttachmentParcelPostXSendFileView.as_view(),
        name="outgoing-download"),
]

app_name = 'feder.parcels'
