from django.contrib import admin
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

    list_display = (
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
        "created",
        "record__case__monitoring",
        # "modified",
        "is_spam",
        # "is_outgoing",
    )
    inlines = [AttachmentInline]
    search_fields = (
        "title",
        # "body",
        "record__case__name",
        "eml",
        "message_id_header",
        "email_from",
        "email_to",
    )
    raw_id_fields = ("author_user", "author_institution", "record")
    list_editable = ("is_spam",)

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
