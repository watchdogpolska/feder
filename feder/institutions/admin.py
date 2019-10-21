from django.contrib import admin
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from .models import Institution, Tag


@admin.register(Institution)
class InstitutionAdmin(VersionAdmin):
    """
        Admin View for Institution
    """

    list_display = ("name", "jst", "email")
    search_fields = ["name"]
    raw_id_fields = ("jst",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_institution_count")

    def get_institution_count(self, obj):
        return obj.institution_count

    get_institution_count.admin_order_field = "institution_count"
    get_institution_count.short_description = _("Institution count")

    def get_queryset(self, *args, **kwargs):
        qs = super(TagAdmin, self).get_queryset(*args, **kwargs)
        return qs.annotate(institution_count=Count("institution"))
