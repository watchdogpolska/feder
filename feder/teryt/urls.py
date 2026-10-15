from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    re_path(_(r"^(?P<slug>[\w-]+)$"), views.JSTDetailView.as_view(), name="details"),
    path(_(""), views.JSTListView.as_view(), name="list"),
    path(_(""), views.JSTListView.as_view(), name="voivodeship"),
    path(
        "voivodeship-autocomplete/",
        views.VoivodeshipAutocomplete.as_view(),
        name="voivodeship-autocomplete",
    ),
    path(
        "county-autocomplete/",
        views.CountyAutocomplete.as_view(),
        name="county-autocomplete",
    ),
    path(
        "community-autocomplete/",
        views.CustomCommunityAutocomplete.as_view(),
        name="community-autocomplete",
    ),
    path(
        "jst-autocomplete/",
        views.JSTAutocomplete.as_view(),
        name="jst-autocomplete",
    ),
]

app_name = "feder.teryt"
