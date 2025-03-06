from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _
from teryt_tree.dal_ext.views import CountyAutocomplete, VoivodeshipAutocomplete

from . import views

urlpatterns = [
    re_path(_(r"^(?P<slug>[\w-]+)$"), views.JSTDetailView.as_view(), name="details"),
    re_path(_(r"^$"), views.JSTListView.as_view(), name="list"),
    re_path(_(r"^$"), views.JSTListView.as_view(), name="voivodeship"),
    path(
        "voivodeship-autocomplete/",
        VoivodeshipAutocomplete.as_view(),
        name="voivodeship-autocomplete",
    ),
    path(
        "county-autocomplete/",
        CountyAutocomplete.as_view(),
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
