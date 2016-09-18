# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r'^$'), views.CaseListView.as_view(),
        name="list"),
    url(_(r'^~create-(?P<monitoring>[\d]+)$'), views.CaseCreateView.as_view(),
        name="create"),
    url(_(r'^(?P<slug>[\w-]+)$'), views.CaseDetailView.as_view(),
        name="details"),
    url(_(r'^(?P<slug>[\w-]+)/~update$'), views.CaseUpdateView.as_view(),
        name="update"),
    url(_(r'^(?P<slug>[\w-]+)/~delete$'), views.CaseDeleteView.as_view(),
        name="delete"),
    url(_(r'^~autocomplete$'), views.CaseAutocomplete.as_view(),
        name="autocomplete"),
]
