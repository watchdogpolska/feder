from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    path("table/", views.MonitoringsTableView.as_view(), name="table"),
    path(
        "monitorings_table_ajax_data/",
        views.MonitoringsAjaxDatatableView.as_view(),
        name="monitorings_table_ajax_data",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/monitoring_cases_table$",
        views.MonitoringCasesTableView.as_view(),
        name="monitoring_cases_table",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/monitoring_cases_table_ajax_data$",
        views.MonitoringCasesAjaxDatatableView.as_view(),
        name="monitoring_cases_table_ajax_data",
    ),
    re_path(_(r"^$"), views.MonitoringListView.as_view(), name="list"),
    re_path(_(r"^~create$"), views.MonitoringCreateView.as_view(), name="create"),
    re_path(_(r"^feed$"), views.MonitoringRssFeed(), name="rss"),
    re_path(_(r"^feed/atom$"), views.MonitoringAtomFeed(), name="atom"),
    re_path(
        _(r"^~autocomplete$"),
        views.MonitoringAutocomplete.as_view(),
        name="autocomplete",
    ),
    re_path(
        _(r"^~autocomplete/user$"),
        views.UserMonitoringAutocomplete.as_view(),
        name="autocomplete_user",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)$"), views.MonitoringDetailView.as_view(), name="details"
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/page-(?P<page>[\d]+)$"),
        view=views.MonitoringDetailView.as_view(),
        name="details",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/letter$"),
        views.LetterListMonitoringView.as_view(),
        name="letters",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/letter/page-(?P<page>[\d]+)$"),
        views.LetterListMonitoringView.as_view(),
        name="letters",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/report$"),
        views.MonitoringReportView.as_view(),
        name="report",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/report/page-(?P<page>[\d]+)$"),
        views.MonitoringReportView.as_view(),
        name="report",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/drafts"),
        views.DraftListMonitoringView.as_view(),
        name="drafts",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/drafts/page-(?P<page>[\d]+)$"),
        views.DraftListMonitoringView.as_view(),
        name="drafts",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/template",
        views.MonitoringTemplateView.as_view(),
        name="template",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/results",
        views.MonitoringResultsView.as_view(),
        name="results",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/answers-categories",
        views.MonitoringAnswersCategoriesView.as_view(),
        name="answers-categories",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/responses-report",
        views.MonitoringResponsesReportView.as_view(),
        name="responses_report",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~update$"),
        views.MonitoringUpdateView.as_view(),
        name="update",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/~results-update$",
        views.MonitoringResultsUpdateView.as_view(),
        name="results_update",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~delete$"),
        views.MonitoringDeleteView.as_view(),
        name="delete",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~permission/~add$"),
        views.PermissionWizard.as_view(),
        name="perm-add",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~permission-(?P<user_pk>[\d]+)$"),
        views.MonitoringUpdatePermissionView.as_view(),
        name="perm-update",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~permission$"),
        views.MonitoringPermissionView.as_view(),
        name="perm",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~assign$"),
        views.MonitoringAssignView.as_view(),
        name="assign",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~mass-message$"),
        views.MassMessageView.as_view(),
        name="mass-message",
    ),
]

app_name = "feder.monitorings"
