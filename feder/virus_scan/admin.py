from django.contrib import admin

from feder.virus_scan.models import Request


@admin.register(Request)
class ScanRequestAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = (
        "id",
        "content_type",
        "content_object",
        "field_name",
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

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
