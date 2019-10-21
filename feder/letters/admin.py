from django.contrib import admin

from .models import Letter, Attachment


class AttachmentInline(admin.StackedInline):
    '''
        Stacked Inline View for Attachment
    '''
    model = Attachment


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    '''
        Admin View for Letter
    '''
    list_display = (
        'title', 'author',
        'created', 'modified',
        'is_draft', 'is_incoming', 'is_spam'
    )
    list_filter = ('created', 'modified', 'is_spam')
    inlines = [
        AttachmentInline,
    ]
    search_fields = ('title', 'body')

    def get_queryset(self, *args, **kwargs):
        qs = super(LetterAdmin, self).get_queryset(*args, **kwargs)
        return qs.with_author()
