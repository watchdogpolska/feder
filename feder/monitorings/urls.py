from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r"^$"), views.MonitoringListView.as_view(), name="list"),
    url(_(r"^~create$"), views.MonitoringCreateView.as_view(), name="create"),
    url(
        _(r"^~autocomplete$"),
        views.MonitoringAutocomplete.as_view(),
        name="autocomplete",
    ),
    url(
        _(r"^~autocomplete/user$"),
        views.UserMonitoringAutocomplete.as_view(),
        name="autocomplete_user",
    ),
    url(_(r"^(?P<slug>[\w-]+)$"), views.MonitoringDetailView.as_view(), name="details"),
    url(
        _(r"^(?P<slug>[\w-]+)/page-(?P<page>[\d]+)$"),
        view=views.MonitoringDetailView.as_view(),
        name="details",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/letter$"),
        views.LetterListMonitoringView.as_view(),
        name="letters",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/letter/page-(?P<page>[\d]+)$"),
        views.LetterListMonitoringView.as_view(),
        name="letters",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/report$"),
        views.MonitoringReportView.as_view(),
        name="report",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/report/page-(?P<page>[\d]+)$"),
        views.MonitoringReportView.as_view(),
        name="report",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/drafts"),
        views.DraftListMonitoringView.as_view(),
        name="drafts",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/drafts/page-(?P<page>[\d]+)$"),
        views.DraftListMonitoringView.as_view(),
        name="drafts",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~update$"),
        views.MonitoringUpdateView.as_view(),
        name="update",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~delete$"),
        views.MonitoringDeleteView.as_view(),
        name="delete",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~permission/~add$"),
        views.PermissionWizard.as_view(),
        name="perm-add",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~permission-(?P<user_pk>[\d]+)$"),
        views.MonitoringUpdatePermissionView.as_view(),
        name="perm-update",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~permission$"),
        views.MonitoringPermissionView.as_view(),
        name="perm",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~assign$"),
        views.MonitoringAssignView.as_view(),
        name="assign",
    ),
]

app_name = "feder.monitorings"
