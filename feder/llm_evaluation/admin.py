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
        "letter_id",
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
        return obj.cost_str

    @admin.display(description="Time used")
    def get_time_used(self, obj):
        return obj.completion_time_str

    @admin.display(description="Letter ID")
    def letter_id(self, obj):
        return obj.evaluated_letter.id


@admin.register(LlmMonitoringRequest)
class LlmMonitoringRequestAdmin(admin.ModelAdmin):
    verbose_name = _("LLM Monitoring Request")
    date_hierarchy = "created"
    list_display = (
        "id",
        "evaluated_monitoring",
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
        return obj.cost_str

    @admin.display(description="Time used")
    def get_time_used(self, obj):
        return obj.completion_time_str
