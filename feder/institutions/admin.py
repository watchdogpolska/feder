from django.contrib import admin
from django.db.models import Count

from .models import Email, Institution, Tag


class EmailInline(admin.StackedInline):
    '''
        Stacked Inline View for Email
    '''
    model = Email


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    '''
        Admin View for Institution
    '''
    list_display = ('name', 'jst', 'get_email_count')
    search_fields = ['name', ]
    raw_id_fields = ('jst', )
    inlines = [
        EmailInline,
    ]

    def get_email_count(self, obj):
        return obj.email_count

    def get_queryset(self, *args, **kwargs):
        qs = super(InstitutionAdmin, self).get_queryset(*args, **kwargs)
        return qs.annotate(email_count=Count('email'))


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_institution_count')

    def get_institution_count(self, obj):
        return obj.institution_count

    def get_queryset(self, *args, **kwargs):
        qs = super(TagAdmin, self).get_queryset(*args, **kwargs)
        return qs.annotate(institution_count=Count('institution'))
