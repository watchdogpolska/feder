# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

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
    url(_(r'^(?P<pk>[\d-]+)$'), views.LetterDetailView.as_view(),
        name="details"),
    url(_(r'^(?P<pk>[\d-]+)-msg$'), views.LetterMessageXSendFileView.as_view(),
        name="download"),
    url(_(r'^attachment/(?P<pk>[\d-]+)/(?P<letter_pk>[\d-]+)'), views.AttachmentXSendFileView.as_view(),
        name="attachment"),
    url(r'^attachment/(?P<pk>[\d-]+)/(?P<letter_pk>[\d-]+)', views.AttachmentXSendFileView.as_view()),
        # no translation for back-ward compatibility
    url(_(r'^(?P<pk>[\d-]+)/~update$'), views.LetterUpdateView.as_view(),
        name="update"),
    url(_(r'^(?P<pk>[\d-]+)/~send'), views.LetterSendView.as_view(),
        name="send"),
    url(_(r'^(?P<pk>[\d-]+)/~delete$'), views.LetterDeleteView.as_view(),
        name="delete"),
    url(_(r'^(?P<pk>[\d-]+)/~reply$'), views.LetterReplyView.as_view(),
        name="reply"),
    url(_(r'^(?P<pk>[\d-]+)/~spam'), views.LetterReportSpamView.as_view(),
        name="spam"),
    url(_(r'^(?P<pk>[\d-]+)/~mark-spam'), views.LetterMarkSpamView.as_view(),
        name="mark_spam"),
    url(_(r'^assign$'), views.UnrecognizedLetterListView.as_view(),
        name="unrecognized_list"),
    url(_(r'^~assign-(?P<pk>[\d-]+)$'), views.AssignLetterFormView.as_view(),
        name="assign"),
    url(_(r'^webhook'), csrf_exempt(views.ReceiveEmail.as_view()), name="webhook"),
]

app_name = 'feder.letters'
