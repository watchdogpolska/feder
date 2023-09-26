from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    re_path(regex=_(r"^$"), view=views.UserListView.as_view(), name="list"),
    # URL pattern for the UserRedirectView
    re_path(
        regex=_(r"^~redirect/$"), view=views.UserRedirectView.as_view(), name="redirect"
    ),
    # URL pattern for the UserDetailView
    re_path(
        regex=_(r"^(?P<username>[\w.@+-]+)/$"),
        view=views.UserDetailView.as_view(),
        name="detail",
    ),
    # URL pattern for the UserUpdateView
    re_path(regex=_(r"^~update/$"), view=views.UserUpdateView.as_view(), name="update"),
    # URL pattern for the UserUpdateView
    re_path(
        regex=_(r"^~autocomplete$"),
        view=views.UserAutocomplete.as_view(),
        name="autocomplete",
    ),
]

app_name = "feder.users"
