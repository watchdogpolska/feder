from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Letter, Attachment, LetterEmailDomain


class AttachmentInline(admin.StackedInline):
    """
    Stacked Inline View for Attachment
    """

    model = Attachment


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    """
    Admin View for Letter
    """

    date_hierarchy = "created"
    list_display = (
        "id",
        "get_record_id",
        "title",
        "get_case",
        "get_monitoring",
        "author",
        "created",
        # "modified",
        "is_draft",
        # "is_incoming",
        "is_outgoing",
        "is_spam",
        "email_from",
        "email_to",
        "eml",
        "message_id_header",
    )
    list_filter = (
        "is_spam",
        # "created",
        "record__case__monitoring",
        # "modified",
        # "is_outgoing",
    )
    inlines = [AttachmentInline]
    search_fields = (
        "id",
        "title",
        # "body",
        "record__case__name",
        "eml",
        "message_id_header",
        "email_from",
        "email_to",
    )
    raw_id_fields = ("author_user", "author_institution", "record")
    # list_editable = ("is_spam",)
    ordering = ("-id",)
    actions = [
        "delete_selected",
        "mark_spam",
        "mark_probable_spam",
        "mark_spam_unknown",
        "mark_non_spam",
    ]

    @admin.display(
        description=_("Record id"),
        ordering="record__id",
    )
    def get_record_id(self, obj):
        if obj.record is None:
            return None
        return obj.record.id

    @admin.display(
        description=_("Case name"),
        ordering="record__case",
    )
    def get_case(self, obj):
        return obj.record.case

    @admin.display(
        description=_("Monitoring name"),
        ordering="record__case__monitoring",
    )
    def get_monitoring(self, obj):
        if obj.record.case is not None:
            return obj.record.case.monitoring
        return None

    @admin.action(description="Mark selected letters as Spam")
    def mark_spam(modeladmin, request, queryset):
        queryset.update(
            is_spam=Letter.SPAM.spam,
            mark_spam_by=request.user,
            mark_spam_at=timezone.now(),
        )

    @admin.action(description="Mark selected letters as Non Spam")
    def mark_non_spam(modeladmin, request, queryset):
        queryset.update(is_spam=Letter.SPAM.non_spam)

    @admin.action(description="Mark selected letters as Spam Unknown")
    def mark_spam_unknown(modeladmin, request, queryset):
        queryset.update(is_spam=Letter.SPAM.unknown)

    @admin.action(description="Mark selected letters as Probable Spam")
    def mark_probable_spam(modeladmin, request, queryset):
        queryset.update(is_spam=Letter.SPAM.probable_spam)

    # def get_queryset(self, *args, **kwargs):
    #     qs = super().get_queryset(*args, **kwargs)
    #     return qs.with_author()


@admin.register(LetterEmailDomain)
class LetterEmailDomainAdmin(admin.ModelAdmin):
    """
    Admin View for LetterEmailDomain
    """

    list_display = (
        "domain_name",
        "is_trusted_domain",
        "is_monitoring_email_to_domain",
        "is_non_spammer_domain",
        "is_spammer_domain",
        "email_to_count",
        "email_from_count",
    )
    list_filter = (
        "is_trusted_domain",
        "is_monitoring_email_to_domain",
        "is_non_spammer_domain",
        "is_spammer_domain",
    )
    search_fields = ("domain_name",)
    ordering = ("-email_from_count",)
    list_editable = ("is_spammer_domain", "is_non_spammer_domain")
