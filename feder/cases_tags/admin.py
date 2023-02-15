from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
    list_display = [
        "pk",
        "name",
        "monitoring",
    ]
    actions = None
