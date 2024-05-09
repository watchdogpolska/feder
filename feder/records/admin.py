import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from .models import Record


class RecordInline(admin.StackedInline):
    """
    Stacked Inline View for Record
    """

    model = Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    # inlines = [RecordInline]
    date_hierarchy = "created"
    list_display = [
        "id",
        "created",
        "case",
        "get_case_id",
        "letters_letter_related",
        "get_letter_id",
        "get_incomingparcelpost_id",
        "get_outgoingparcelpost_id",
    ]
    # list_filter = []
    search_fields = [
        "id",
        "case__id",
        "case__name",
        "letters_letter_related__id",
        "letters_letter_related__title",
    ]
    ordering = ("-created",)
    actions = ["delete_selected", "export_as_csv"]

    @admin.display(
        description=_("Letter id"),
        ordering="letters_letters__id",
    )
    def get_letter_id(self, obj):
        if obj.letters_letter_related is None:
            return None
        return obj.letters_letter_related.id

    @admin.display(
        description=_("Case id"),
        ordering="case__id",
    )
    def get_case_id(self, obj):
        if obj.case is None:
            return None
        return obj.case.id

    @admin.display(
        description=_("Incoming parcel id"),
        ordering="parcels_incomingparcelposts__id",
    )
    def get_incomingparcelpost_id(self, obj):
        if obj.parcels_incomingparcelpost_related is None:
            return None
        return obj.parcels_incomingparcelpost_related.id

    @admin.display(
        description=_("Outgoing parcel id"),
        ordering="parcels_outgoingparcelposts__id",
    )
    def get_outgoingparcelpost_id(self, obj):
        if obj.parcels_outgoingparcelpost_related is None:
            return None
        return obj.parcels_outgoingparcelpost_related.id

    @admin.action(description="Export selected records as CSV")
    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="selected_records_export.csv"'
        )

        writer = csv.writer(response)
        # Write the headers
        writer.writerow(queryset.model._meta.fields)
        # Write the data
        headers = [field.name for field in queryset.model._meta.fields]
        data = queryset.values_list(*headers)
        writer.writerows(data)

        return response

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
