from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from reversion.admin import VersionAdmin

from .models import Monitoring


@admin.register(Monitoring)
class MonitoringAdmin(VersionAdmin, GuardedModelAdmin):
    """
        Admin View for Monitoring
    """

    list_display = ("name", "user")
    search_fields = ["name"]
