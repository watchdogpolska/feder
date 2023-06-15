from django.contrib import admin

# Register your models here.
from feder.letters.logs.models import EmailLog, LogRecord


class LogRecordInline(admin.StackedInline):
    """
    Stacked Inline View for LogRecord
    """

    model = LogRecord
    readonly_fields = ["data", "created", "modified"]


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """
    Admin View for EmailLog
    """

    list_display = ("id", "created", "case", "get_institution", "email_id", "status")
    search_fields = (
        "id",
        "case__name",
        "case__institution__name",
    )
    list_filter = ("status", "case__monitoring")
    inlines = [LogRecordInline]
    ordering = ("-id",)
    actions = None

    def get_institution(self, obj):
        return obj.case.institution

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
