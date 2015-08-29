# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.LetterListView.as_view(),
        name="list"),
    url(r'^~create-(?P<case_pk>[\d-]+)$', views.LetterCreateView.as_view(),
        name="create"),
    url(r'^letter-(?P<pk>[\d-]+)$', views.LetterDetailView.as_view(),
        name="details"),
    url(r'^letter-(?P<pk>[\d-]+)/~update$', views.LetterUpdateView.as_view(),
        name="update"),
    url(r'^letter-(?P<pk>[\d-]+)/~delete$', views.LetterDeleteView.as_view(),
        name="delete"),
]
