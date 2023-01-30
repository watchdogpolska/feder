from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    re_path(_(r"^$"), views.InstitutionListView.as_view(), name="list"),
    re_path(_(r"^~create$"), views.InstitutionCreateView.as_view(), name="create"),
    re_path(
        _(r"^(?P<slug>[\w-]+)$"),
        view=views.InstitutionDetailView.as_view(),
        name="details",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/(?P<page>[\d]+)$"),
        views.InstitutionDetailView.as_view(),
        name="details",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~update$"),
        views.InstitutionUpdateView.as_view(),
        name="update",
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~delete$"),
        views.InstitutionDeleteView.as_view(),
        name="delete",
    ),
    re_path(
        _(r"^~autocomplete$"),
        views.InstitutionAutocomplete.as_view(),
        name="autocomplete",
    ),
    re_path(
        _(r"^~autocomplete-tag$"),
        views.TagAutocomplete.as_view(),
        name="tag_autocomplete",
    ),
]

app_name = "feder.institutions"
