from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost


@admin.register(IncomingParcelPost)
class IncomingParcelPostAdmin(admin.ModelAdmin):
    """
    Admin View for IncomingParcelPostAdmin
    """

    date_hierarchy = "created"
    list_display = (
        "id",
        "get_record_id",
        "title",
        "receive_date",
        "created",
        "content",
        "sender",
        "get_case",
        "get_monitoring",
        "comment",
    )
    list_filter = ("record__case__monitoring",)
    search_fields = (
        "id",
        "title",
        "record__case__name",
        "record__case__monitoring__name",
    )
    raw_id_fields = ("record",)
    ordering = ("-id",)
    actions = []

    @admin.display(
        description=_("Record id"),
        ordering="record__id",
    )
    def get_record_id(self, obj):
        if obj.record is None:
            return None
        return obj.record.id

    @admin.display(
        description=_("Case name"),
        ordering="record__case",
    )
    def get_case(self, obj):
        return obj.record.case

    @admin.display(
        description=_("Monitoring name"),
        ordering="record__case__monitoring",
    )
    def get_monitoring(self, obj):
        if obj.record.case is not None:
            return obj.record.case.monitoring
        return None


@admin.register(OutgoingParcelPost)
class OutgoingParcelPostAdmin(admin.ModelAdmin):
    """
    Admin View for OutgoingParcelPostAdmin
    """

    date_hierarchy = "created"
    list_display = (
        "id",
        "get_record_id",
        "title",
        "post_date",
        "created",
        "content",
        "recipient",
        "get_case",
        "get_monitoring",
    )
    list_filter = ("record__case__monitoring",)
    search_fields = (
        "id",
        "title",
        "record__case__name",
        "record__case__monitoring__name",
    )
    raw_id_fields = ("record",)
    ordering = ("-id",)
    actions = []

    @admin.display(
        description=_("Record id"),
        ordering="record__id",
    )
    def get_record_id(self, obj):
        if obj.record is None:
            return None
        return obj.record.id

    @admin.display(
        description=_("Case name"),
        ordering="record__case",
    )
    def get_case(self, obj):
        return obj.record.case

    @admin.display(
        description=_("Monitoring name"),
        ordering="record__case__monitoring",
    )
    def get_monitoring(self, obj):
        if obj.record.case is not None:
            return obj.record.case.monitoring
        return None
