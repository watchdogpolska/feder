from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from .models import Institution, Tag


@admin.register(Institution)
class InstitutionAdmin(VersionAdmin):
    """
    Admin View for Institution
    """

    list_display = (
        "id",
        "name",
        "archival",
        "jst",
        "get_teryt",
        "email",
        "regon",
        "get_tags",
    )
    search_fields = ["name", "tags__name", "jst__name", "jst__id", "email", "regon"]
    list_filter = ("tags", "archival")
    raw_id_fields = ("jst",)
    actions = ["mark_archival", "mark_non_archival"]

    @admin.display(description=_("Institution tags"))
    def get_tags(self, obj):
        return ", ".join(obj.tags.values_list("name", flat=True))

    @admin.display(description=_("Teryt code"))
    def get_teryt(self, obj):
        return obj.jst.id

    @admin.action(description=_("Mark selected institution as archival"))
    def mark_archival(self, request, queryset):
        queryset.update(
            archival=True,
        )
        for obj in queryset:
            self.log_change(request, obj, _("Mark selected institution as archival"))

    @admin.action(description=_("Mark selected institution as NON archival"))
    def mark_non_archival(self, request, queryset):
        queryset.update(
            archival=False,
        )
        for obj in queryset:
            self.log_change(
                request, obj, _("Mark selected institution as NON archival")
            )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_institution_count")
    search_fields = ["name"]
    actions = None

    @admin.display(
        description=_("Institution count"),
        ordering="institution_count",
    )
    def get_institution_count(self, obj):
        return obj.institution_count

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.annotate(institution_count=Count("institution"))
