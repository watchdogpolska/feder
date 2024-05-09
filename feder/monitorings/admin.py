from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from reversion.admin import VersionAdmin

from .models import Monitoring


@admin.register(Monitoring)
class MonitoringAdmin(VersionAdmin, GuardedModelAdmin):
    """
    Admin View for Monitoring
    """

    list_display = (
        "id",
        "name",
        "user",
        "is_public",
        "hide_new_cases",
        "notify_alert",
        "domain",
    )
    search_fields = ["id", "name"]
    actions = None
    ordering = [
        "-id",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
