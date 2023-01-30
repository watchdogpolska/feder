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

    list_display = ("case", "email_id", "status")
    list_filter = ("status", "case__monitoring")
    inlines = [LogRecordInline]
    readonly_fields = ["created", "modified"]
