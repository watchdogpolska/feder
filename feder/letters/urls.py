from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    re_path(_(r"^$"), views.LetterListView.as_view(), name="list"),
    re_path(_(r"^feed$"), views.LetterRssFeed(), name="rss"),
    re_path(_(r"^feed/atom$"), views.LetterAtomFeed(), name="atom"),
    re_path(
        _(r"^feed/monitoring-(?P<monitoring_pk>[\d-]+)/$"),
        views.LetterMonitoringRssFeed(),
        name="rss",
    ),
    re_path(
        _(r"^feed/monitoring-(?P<monitoring_pk>[\d-]+)/atom$"),
        views.LetterMonitoringAtomFeed(),
        name="atom",
    ),
    re_path(
        _(r"^feed/case-(?P<case_pk>[\d-]+)/$"), views.LetterCaseRssFeed(), name="rss"
    ),
    re_path(
        _(r"^feed/case-(?P<case_pk>[\d-]+)/atom$"),
        views.LetterCaseAtomFeed(),
        name="atom",
    ),
    re_path(
        _(r"^~create-(?P<case_pk>[\d-]+)$"),
        views.LetterCreateView.as_view(),
        name="create",
    ),
    re_path(_(r"^(?P<pk>[\d-]+)$"), views.LetterDetailView.as_view(), name="details"),
    re_path(
        _(r"^(?P<pk>[\d-]+)-msg$"),
        views.LetterMessageXSendFileView.as_view(),
        name="download",
    ),
    re_path(
        r"^attachment/(?P<pk>[\d-]+)/(?P<letter_pk>[\d-]+)/~scan",
        views.AttachmentRequestCreateView.as_view(),
        name="scan",
    ),
    re_path(
        _(r"^attachment/(?P<pk>[\d-]+)/(?P<letter_pk>[\d-]+)$"),
        views.AttachmentXSendFileView.as_view(),
        name="attachment",
    ),
    re_path(
        r"^attachment/(?P<pk>[\d-]+)/(?P<letter_pk>[\d-]+)$",
        views.AttachmentXSendFileView.as_view(),
    ),  # no translation for back-ward compatibility
    re_path(
        _(r"^(?P<pk>[\d-]+)/~update$"), views.LetterUpdateView.as_view(), name="update"
    ),
    re_path(_(r"^(?P<pk>[\d-]+)/~send"), views.LetterSendView.as_view(), name="send"),
    re_path(
        _(r"^(?P<pk>[\d-]+)/~delete$"), views.LetterDeleteView.as_view(), name="delete"
    ),
    re_path(
        _(r"^(?P<pk>[\d-]+)/~reply$"), views.LetterReplyView.as_view(), name="reply"
    ),
    re_path(
        r"^(?P<pk>[\d-]+)/~resend$", views.LetterResendView.as_view(), name="resend"
    ),  # no translation for test compatibility
    re_path(
        _(r"^(?P<pk>[\d-]+)/~spam"), views.LetterReportSpamView.as_view(), name="spam"
    ),
    re_path(
        _(r"^(?P<pk>[\d-]+)/~mark-spam"),
        views.LetterMarkSpamView.as_view(),
        name="mark_spam",
    ),
    re_path(
        _(r"^assign$"),
        views.UnrecognizedLetterListView.as_view(),
        name="unrecognized_list",
    ),
    re_path(
        _(r"^~assign-(?P<pk>[\d-]+)$"),
        views.AssignLetterFormView.as_view(),
        name="assign",
    ),
    re_path(_(r"^webhook$"), csrf_exempt(views.ReceiveEmail.as_view()), name="webhook"),
]

app_name = "feder.letters"
