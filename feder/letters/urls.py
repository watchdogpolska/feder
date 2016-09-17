# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url

from . import views

urlpatterns = [
    url(_(r'^$'), views.LetterListView.as_view(),
        name="list"),
    url(_(r'^~create-(?P<case_pk>[\d-]+)$'), views.LetterCreateView.as_view(),
        name="create"),
    url(_(r'^letter-(?P<pk>[\d-]+)$'), views.LetterDetailView.as_view(),
        name="details"),
    url(_(r'^letter-(?P<pk>[\d-]+)/~update$'), views.LetterUpdateView.as_view(),
        name="update"),
    url(_(r'^letter-(?P<pk>[\d-]+)/~delete$'), views.LetterDeleteView.as_view(),
        name="delete"),
    url(_(r'^letter-(?P<pk>[\d-]+)/~reply$'), views.LetterReplyView.as_view(),
        name="reply"),
]
