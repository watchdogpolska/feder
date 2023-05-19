from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from reversion.admin import VersionAdmin

from .models import Case, Alias


@admin.register(Case)
class CaseAdmin(VersionAdmin, GuardedModelAdmin):
    """
    Admin View for Case
    """

    list_display = (
        "id",
        "name",
        "user",
        "monitoring",
        "institution",
        "email",
        "confirmation_received",
        "response_received",
        "is_quarantined",
    )
    search_fields = [
        "id",
        "name",
        "user__username",
        "monitoring__name",
        "institution__name",
        "email",
        "tags__name",
    ]
    list_filter = [
        "confirmation_received",
        "response_received",
        "is_quarantined",
    ]
    actions = None


@admin.register(Alias)
class AliasAdmin(VersionAdmin, GuardedModelAdmin):
    """
    Admin View for Alias
    """

    list_display = (
        "case",
        "email",
    )
    search_fields = ["case"]
    actions = None
