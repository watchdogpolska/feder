from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    re_path(_(r"^$"), views.CaseListView.as_view(), name="list"),
    re_path(
        _(r"^~create-(?P<monitoring>[\d]+)$"),
        views.CaseCreateView.as_view(),
        name="create",
    ),
    re_path(_(r"^(?P<slug>[\w-]+)$"), views.CaseDetailView.as_view(), name="details"),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~update$"), views.CaseUpdateView.as_view(), name="update"
    ),
    re_path(
        _(r"^(?P<slug>[\w-]+)/~delete$"), views.CaseDeleteView.as_view(), name="delete"
    ),
    re_path(
        _(r"^~autocomplete$"), views.CaseAutocomplete.as_view(), name="autocomplete"
    ),
    re_path(
        _(r"^~autocomplete/~find$"),
        views.CaseFindAutocomplete.as_view(),
        name="autocomplete-find",
    ),
]

app_name = "feder.cases"
