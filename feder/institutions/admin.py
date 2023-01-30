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

    list_display = ("name", "jst", "email")
    search_fields = ["name", "tags__name"]
    raw_id_fields = ("jst",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_institution_count")

    @admin.display(
        description=_("Institution count"),
        ordering="institution_count",
    )
    def get_institution_count(self, obj):
        return obj.institution_count

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.annotate(institution_count=Count("institution"))
