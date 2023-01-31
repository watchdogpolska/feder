from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)$"),
        views.TagListView.as_view(),
        name="list",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)/~create$"),
        views.TagCreateView.as_view(),
        name="create",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)/~autocomplete$"),
        views.TagAutocomplete.as_view(),
        name="autocomplete",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)/(?P<pk>[\d]+)$"),
        views.TagDetailView.as_view(),
        name="details",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)/(?P<pk>[\d]+)/~update$"),
        views.TagUpdateView.as_view(),
        name="update",
    ),
    re_path(
        _(r"^monitoring-(?P<monitoring>[\d]+)/(?P<pk>[\d]+)/~delete$"),
        views.TagDeleteView.as_view(),
        name="delete",
    ),
]

app_name = "feder.cases_tags"
