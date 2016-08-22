# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from teryt_tree.dal_ext.views import (CommunityAutocomplete,
                                      CountyAutocomplete,
                                      VoivodeshipAutocomplete)

from . import views

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)$', views.JSTDetailView.as_view(), name="details"),
    url(r'^$', views.JSTListView.as_view(), name="list"),
    url(r'^$', views.JSTListView.as_view(), name="voivodeship"),
    url(r'^voivodeship-autocomplete/$', VoivodeshipAutocomplete.as_view(),
        name='voivodeship-autocomplete',),
    url(r'^county-autocomplete/$', CountyAutocomplete.as_view(),
        name='county-autocomplete',),
    url(r'^community-autocomplete/$', CommunityAutocomplete.as_view(),
        name='community-autocomplete',),
]
