from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import (
    LlmLetterRequest,
    LlmMonitoringCost,
    LlmMonitoringRequest,
    LlmMonthlyCost,
)


@admin.register(LlmLetterRequest)
class LlmLetterRequestAdmin(admin.ModelAdmin):
    verbose_name = _("LLM Letter Request")
    date_hierarchy = "created"
    list_display = (
        "id",
        "name",
        "evaluated_letter",
        "letter_id",
        "engine_name",
        "status",
        "get_cost",
        "get_time_used",
        "created",
    )
    list_filter = ("engine_name", "status", "name")
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
        "name",
        "evaluated_monitoring",
        "engine_name",
        "status",
        "get_cost",
        "get_time_used",
        "created",
    )
    list_filter = ("engine_name", "status", "name")
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


@admin.register(LlmMonthlyCost)
class LlmMonthlyCostAdmin(admin.ModelAdmin):
    verbose_name = _("LLM Monthly Cost")
    list_display = (
        "id",
        "year_month",
        "engine_name",
        "formatted_cost",
    )
    actions = []
    ordering = ("-id",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Cost in USD")
    def formatted_cost(self, obj):
        return f"{obj.cost:.5f}"[:7]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        LlmMonthlyCost.objects.all().delete()
        data = LlmMonthlyCost.get_costs_dict()
        for item in data:
            LlmMonthlyCost.objects.get_or_create(**item)
        return super().get_queryset(request)


@admin.register(LlmMonitoringCost)
class LlmMonitoringCostAdmin(admin.ModelAdmin):
    verbose_name = _("LLM Monitoring Cost")
    list_display = (
        "id",
        "monitoring_id",
        "monitoring_name",
        "engine_name",
        "formatted_cost",
    )
    actions = []
    ordering = ("-id",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Cost in USD")
    def formatted_cost(self, obj):
        return f"{obj.cost:.5f}"[:7]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        LlmMonitoringCost.objects.all().delete()
        data = LlmMonitoringCost.get_costs_dict()
        for item in data:
            LlmMonitoringCost.objects.get_or_create(**item)
        return super().get_queryset(request)
