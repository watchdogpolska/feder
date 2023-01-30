from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)$"),
        views.AlertListView.as_view(),
        name="list",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)/~create$"),
        views.AlertCreateView.as_view(),
        name="create",
    ),
    re_path(_(r"^(?P<pk>[\d]+)$"), views.AlertDetailView.as_view(), name="details"),
    re_path(
        _(r"^(?P<pk>[\d]+)/~update$"), views.AlertUpdateView.as_view(), name="update"
    ),
    re_path(
        _(r"^(?P<pk>[\d]+)/~delete$"), views.AlertDeleteView.as_view(), name="delete"
    ),
    re_path(
        _(r"^(?P<pk>[\d]+)/~status$"), views.AlertStatusView.as_view(), name="status"
    ),
]

app_name = "feder.alerts"
