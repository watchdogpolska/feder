from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import JednostkaAdministracyjna


class JednostkaAdministracyjnaAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "slug", "updated_on", "name", "category", "parent"]
    list_display = ["id", "name", "slug", "category", "parent", "updated_on", "active"]
    list_display_links = ["id", "name"]
    list_filter = ["category", "active"]
    search_fields = ["id", "name", "slug"]
    date_hierarchy = "updated_on"
    actions = ["set_inactive", "set_active"]
    ordering = ("id",)

    @admin.action(description=_("Activate selected JSTs"))
    def set_active(self, request, queryset):
        queryset.update(active=True)
        for obj in queryset:
            self.log_change(request, obj, _("Activate selected JSTs"))

    @admin.action(description=_("Deactivate selected JSTs"))
    def set_inactive(self, request, queryset):
        queryset.update(active=False)
        for obj in queryset:
            self.log_change(request, obj, _("Deactivate selected JSTs"))

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.unregister(JednostkaAdministracyjna)  # unregister original from teryt_tree
admin.site.register(JednostkaAdministracyjna, JednostkaAdministracyjnaAdmin)
