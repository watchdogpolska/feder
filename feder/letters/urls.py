# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r'^$'), views.LetterListView.as_view(),
        name="list"),
    url(_(r'^feed$'), views.LetterRssFeed(),
        name="rss"),
    url(_(r'^feed/atom$'), views.LetterAtomFeed(),
        name="atom"),
    url(_(r'^feed/monitoring-(?P<monitoring_pk>[\d-]+)/$'), views.LetterMonitoringRssFeed(),
        name="rss"),
    url(_(r'^feed/monitoring-(?P<monitoring_pk>[\d-]+)/atom$'), views.LetterMonitoringAtomFeed(),
        name="atom"),
    url(_(r'^feed/case-(?P<case_pk>[\d-]+)/$'), views.LetterCaseRssFeed(),
        name="rss"),
    url(_(r'^feed/case-(?P<case_pk>[\d-]+)/atom$'), views.LetterCaseAtomFeed(),
        name="atom"),
    url(_(r'^~create-(?P<case_pk>[\d-]+)$'), views.LetterCreateView.as_view(),
        name="create"),
    url(_(r'^(?P<pk>[\d-]+)$'), views.LetterDetailView.as_view(),
        name="details"),
    url(_(r'^(?P<pk>[\d-]+)/~update$'), views.LetterUpdateView.as_view(),
        name="update"),
    url(_(r'^(?P<pk>[\d-]+)/~send'), views.LetterSendView.as_view(),
        name="send"),
    url(_(r'^(?P<pk>[\d-]+)/~delete$'), views.LetterDeleteView.as_view(),
        name="delete"),
    url(_(r'^(?P<pk>[\d-]+)/~reply$'), views.LetterReplyView.as_view(),
        name="reply"),
    url(_(r'^(?P<pk>[\d-]+)/~spam'), views.ReportSpamView.as_view(),
        name="spam"),
]
