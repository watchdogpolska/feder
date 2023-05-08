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

    list_display = ("id", "name", "jst", "get_teryt", "email", "regon", "get_tags")
    search_fields = ["name", "tags__name", "jst__name", "jst__id", "email", "regon"]
    list_filter = ("tags",)
    raw_id_fields = ("jst",)
    actions = None

    def get_tags(self, obj):
        return ", ".join(obj.tags.values_list("name", flat=True))

    def get_teryt(self, obj):
        return obj.jst.id


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_institution_count")
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
