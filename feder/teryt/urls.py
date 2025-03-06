from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from teryt_tree.dal_ext.views import CountyAutocomplete, VoivodeshipAutocomplete

from . import views

urlpatterns = [
    re_path(_(r"^(?P<slug>[\w-]+)$"), views.JSTDetailView.as_view(), name="details"),
    re_path(_(r"^$"), views.JSTListView.as_view(), name="list"),
    re_path(_(r"^$"), views.JSTListView.as_view(), name="voivodeship"),
    re_path(
        r"^voivodeship-autocomplete/$",
        VoivodeshipAutocomplete.as_view(),
        name="voivodeship-autocomplete",
    ),
    re_path(
        r"^county-autocomplete/$",
        CountyAutocomplete.as_view(),
        name="county-autocomplete",
    ),
    re_path(
        r"^community-autocomplete/$",
        views.CustomCommunityAutocomplete.as_view(),
        name="community-autocomplete",
    ),
    re_path(
        r"^jst-autocomplete/$",
        views.JSTAutocomplete.as_view(),
        name="jst-autocomplete",
    ),
]

app_name = "feder.teryt"
