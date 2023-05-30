from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^~create-incoming-(?P<case_pk>\d+)$",
        views.IncomingParcelPostCreateView.as_view(),
        name="incoming-create",
    ),
    re_path(
        r"^incoming-(?P<pk>[\w-]+)$",
        views.IncomingParcelPostDetailView.as_view(),
        name="incoming-details",
    ),
    re_path(
        r"^incoming-(?P<pk>[\w-]+)/~update$",
        views.IncomingParcelPostUpdateView.as_view(),
        name="incoming-update",
    ),
    re_path(
        r"^incoming-(?P<pk>[\w-]+)/~delete$",
        views.IncomingParcelPostDeleteView.as_view(),
        name="incoming-delete",
    ),
    re_path(
        r"^incoming-(?P<pk>[\w-]+)/~download$",
        views.IncomingAttachmentParcelPostXSendFileView.as_view(),
        name="incoming-download",
    ),
    re_path(
        r"^~create-outgoing-(?P<case_pk>\d+)$",
        views.OutgoingParcelPostCreateView.as_view(),
        name="outgoing-create",
    ),
    re_path(
        r"^outgoing-(?P<pk>[\w-]+)$",
        views.OutgoingParcelPostDetailView.as_view(),
        name="outgoing-details",
    ),
    re_path(
        r"^outgoing-(?P<pk>[\w-]+)/~update$",
        views.OutgoingParcelPostUpdateView.as_view(),
        name="outgoing-update",
    ),
    re_path(
        r"^outgoing-(?P<pk>[\w-]+)/~delete$",
        views.OutgoingParcelPostDeleteView.as_view(),
        name="outgoing-delete",
    ),
    re_path(
        r"^outgoing-(?P<pk>[\w-]+)/~download$",
        views.OutgoingAttachmentParcelPostXSendFileView.as_view(),
        name="outgoing-download",
    ),
]

app_name = "feder.parcels"
