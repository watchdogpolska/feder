# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
   url(r'^$', views.InstitutionListView.as_view(), name="list"),
   url(r'^institution-(?P<slug>[\w-]+)$', views.InstitutionDetailView.as_view(), name="details"),
]
