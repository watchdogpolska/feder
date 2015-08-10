# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
   url(r'^$', views.JSTListView.as_view(), name="home"),
   url(r'^(?P<slug>[\w-]+)$', views.JSTDetailView.as_view(), name="details"),
]
