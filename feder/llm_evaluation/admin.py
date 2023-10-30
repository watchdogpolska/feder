from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import LlmLetterRequest, LlmMonitoringRequest


@admin.register(LlmLetterRequest)
class LlmLetterRequestAdmin(admin.ModelAdmin):
    verbose_name = _("LLM Letter Request")
    date_hierarchy = "created"
    list_display = (
        "id",
        "evaluated_letter",
        "engine_name",
        "status",
        "get_cost",
        "get_time_used",
        "created",
    )
    list_filter = (
        "engine_name",
        "status",
    )
    actions = []

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Cost")
    def get_cost(self, obj):
        return f"${obj.get_cost():.5f}"

    @admin.display(description="Time used")
    def get_time_used(self, obj):
        return f"{obj.get_time_used():.2f}s"
