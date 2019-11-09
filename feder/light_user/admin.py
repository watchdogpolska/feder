from django.contrib import admin

# Register your models here.
from feder.light_user.models import LightUser


@admin.register(LightUser)
class LightUserAdmin(admin.ModelAdmin):
    """
        Admin View for LightUser
    """

    list_display = ("ip", "user", "created", "modified")
