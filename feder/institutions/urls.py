from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r"^$"), views.InstitutionListView.as_view(), name="list"),
    url(_(r"^~create$"), views.InstitutionCreateView.as_view(), name="create"),
    url(
        _(r"^(?P<slug>[\w-]+)$"),
        view=views.InstitutionDetailView.as_view(),
        name="details",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/(?P<page>[\d]+)$"),
        views.InstitutionDetailView.as_view(),
        name="details",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~update$"),
        views.InstitutionUpdateView.as_view(),
        name="update",
    ),
    url(
        _(r"^(?P<slug>[\w-]+)/~delete$"),
        views.InstitutionDeleteView.as_view(),
        name="delete",
    ),
    url(
        _(r"^~autocomplete$"),
        views.InstitutionAutocomplete.as_view(),
        name="autocomplete",
    ),
    url(
        _(r"^~autocomplete-tag$"),
        views.TagAutocomplete.as_view(),
        name="tag_autocomplete",
    ),
]

app_name = "feder.institutions"
