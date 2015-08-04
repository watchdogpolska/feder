from django.db.models import Count
from django.contrib import admin
from .models import Institution, Email, Tag


class EmailInline(admin.StackedInline):
    '''
        Stacked Inline View for Email
    '''
    model = Email


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
admin.site.register(Institution, InstitutionAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_institution_count')

    def get_institution_count(self, obj):
        return obj.institution_count

    def get_queryset(self, *args, **kwargs):
        qs = super(TagAdmin, self).get_queryset(*args, **kwargs)
        return qs.annotate(institution_count=Count('institution'))
admin.site.register(Tag, TagAdmin)
