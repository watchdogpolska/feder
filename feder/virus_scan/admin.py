from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from feder.letters.models import Letter
from feder.virus_scan.models import Request, EngineApiKey


@admin.register(Request)
class ScanRequestAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = (
        "id",
        "content_type",
        "object_id",
        "get_letter_is_spam",
        "engine_name",
        "status",
        "created",
        "modified",
    )
    ordering = ("-id",)
    list_filter = ("engine_name", "status", "modified")
    actions = None

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.prefetch_related("content_object").select_related("content_type")

    @admin.display(description=_("Letter is spam"))
    def get_letter_is_spam(self, obj):
        if hasattr(obj.content_object, "letter"):
            return Letter.SPAM._display_map[obj.content_object.letter.is_spam]
        return None

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EngineApiKey)
class EngineApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "engine",
        "prevention_limit",
        "prevention_remaining",
        "prevention_interval_sec",
        "prevention_reset_at",
        "last_used",
    )
    ordering = ("-id",)
    list_filter = ("engine",)
    readonly_fields = (
        "prevention_limit",
        "prevention_remaining",
        "prevention_interval_sec",
        "prevention_reset_at",
        "last_used",
    )
