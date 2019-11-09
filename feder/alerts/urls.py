from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)$"),
        views.AlertListView.as_view(),
        name="list",
    ),
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)/~create$"),
        views.AlertCreateView.as_view(),
        name="create",
    ),
    url(_(r"^(?P<pk>[\d]+)$"), views.AlertDetailView.as_view(), name="details"),
    url(_(r"^(?P<pk>[\d]+)/~update$"), views.AlertUpdateView.as_view(), name="update"),
    url(_(r"^(?P<pk>[\d]+)/~delete$"), views.AlertDeleteView.as_view(), name="delete"),
    url(_(r"^(?P<pk>[\d]+)/~status$"), views.AlertStatusView.as_view(), name="status"),
]

app_name = "feder.alerts"
