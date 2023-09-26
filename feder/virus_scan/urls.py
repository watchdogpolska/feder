from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    re_path(
        _(r"^webhook/$"),
        view=csrf_exempt(views.RequestWebhookView.as_view()),
        name="webhook",
    ),
]

app_name = "feder.virus_scan"
