from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)$"),
        views.TagListView.as_view(),
        name="list",
    ),
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)/~create$"),
        views.TagCreateView.as_view(),
        name="create",
    ),
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)/~autocomplete$"),
        views.TagAutocomplete.as_view(),
        name="autocomplete",
    ),
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)/(?P<pk>[\d]+)$"),
        views.TagDetailView.as_view(),
        name="details",
    ),
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)/(?P<pk>[\d]+)/~update$"),
        views.TagUpdateView.as_view(),
        name="update",
    ),
    url(
        _(r"^monitoring-(?P<monitoring>[\d]+)/(?P<pk>[\d]+)/~delete$"),
        views.TagDeleteView.as_view(),
        name="delete",
    ),
]

app_name = "feder.cases_tags"
