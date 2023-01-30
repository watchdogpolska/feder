from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    re_path(
        _(r"^case-(?P<case_pk>[\d-]+)$"),
        views.EmailLogCaseListView.as_view(),
        name="list",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring_pk>[\d-]+)$"),
        views.EmailLogMonitoringListView.as_view(),
        name="list",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring_pk>[\d-]+)/export$"),
        views.EmailLogMonitoringCsvView.as_view(),
        name="export",
    ),
    re_path(_(r"^log-(?P<pk>[\d-]+)$"), views.EmailLogDetailView.as_view(), name="detail"),
]

app_name = "feder.letters.logs"
