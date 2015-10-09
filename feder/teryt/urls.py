# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)$', views.JSTDetailView.as_view(), name="details"),
    url(r'^$', views.JSTListView.as_view(), name="list"),
    url(r'^$', views.JSTListView.as_view(), name="voivodeship"),
]
