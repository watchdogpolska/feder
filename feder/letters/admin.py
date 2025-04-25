from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Subquery, OuterRef, IntegerField, Exists
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from feder.llm_evaluation.prompts import letter_categories_list
from feder.virus_scan.models import Request

from .models import Attachment, Letter, LetterEmailDomain, ReputableLetterEmailTLD


class LetterDirectionListFilter(admin.SimpleListFilter):
    title = _("Letter Direction")  # Displayed in the admin sidebar
    parameter_name = "letter_direction_filter"  # The URL parameter name

    def lookups(self, request, model_admin):
        # Return the filter options as a list of tuples
        return (
            ("outgoing", _("Outgoing")),
            ("incoming", _("Incoming")),
        )

    def queryset(self, request, queryset):
        # Apply the filter to the queryset based on the selected option
        if self.value() == "outgoing":
            return queryset.is_outgoing()
        elif self.value() == "incoming":
            return queryset.is_incoming()


class LetterLlmEvaluationListFilter(admin.SimpleListFilter):
    title = _("Letter LLM Evaluation")  # Displayed in the admin sidebar
    parameter_name = "letter_llm_evaluation_filter"  # The URL parameter name

    def lookups(self, request, model_admin):
        # Return the filter options as a list of tuples
        return list(
            (
                " ".join(item.format(institution=" ... ").replace("\n", "").split())[
                    :20
                ],
                " ".join(item.format(institution=" ... ").replace("\n", "").split()),
            )
            for item in letter_categories_list
        )

    def queryset(self, request, queryset):
        # Apply the filter to the queryset based on the selected option
        if self.value():
            return queryset.filter(ai_evaluation__startswith=self.value())
        return queryset


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
        "get_outgoing",
        "get_delivery_status",
        "is_spam",
        "ai_evaluation",
        "email_from",
        "email_to",
        "eml",
        "message_id_header",
    )
    list_filter = (
        "is_spam",
        LetterLlmEvaluationListFilter,
        LetterDirectionListFilter,
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
    # raw_id_fields = ("author_user", "author_institution", "record")
    # list_editable = ("is_spam",)
    ordering = ("-id",)
    actions = [
        "delete_selected",
        "mark_spam",
        "mark_probable_spam",
        "mark_spam_unknown",
        "mark_non_spam",
    ]
    readonly_fields = ("author_user", "author_institution", "record")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(
        description=_("Record id"),
        ordering="record__id",
    )
    def get_record_id(self, obj):
        if obj.record is None:
            return None
        return obj.record.id

    @admin.display(
        description=_("Is outgoing"),
        boolean=True,
    )
    def get_outgoing(self, obj):
        return obj.is_outgoing

    @admin.display(
        description=_("Delivery Status"),
    )
    def get_delivery_status(self, obj):
        return obj.emaillog.status_verbose

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

    @admin.action(description=_("Mark selected letters as Spam"))
    def mark_spam(modeladmin, request, queryset):
        queryset.update(
            is_spam=Letter.SPAM.spam,
            mark_spam_by=request.user,
            mark_spam_at=timezone.now(),
        )

    @admin.action(description=_("Mark selected letters as Non Spam"))
    def mark_non_spam(modeladmin, request, queryset):
        queryset.update(is_spam=Letter.SPAM.non_spam)

    @admin.action(description=_("Mark selected letters as Spam Unknown"))
    def mark_spam_unknown(modeladmin, request, queryset):
        queryset.update(is_spam=Letter.SPAM.unknown)

    @admin.action(description=_("Mark selected letters as Probable Spam"))
    def mark_probable_spam(modeladmin, request, queryset):
        queryset.update(is_spam=Letter.SPAM.probable_spam)

    # def get_queryset(self, *args, **kwargs):
    #     qs = super().get_queryset(*args, **kwargs)
    #     return qs.with_author()


class AttachmentLetterSpamFilter(admin.SimpleListFilter):
    title = _("Letter is spam")  # Displayed in the admin sidebar
    parameter_name = "letter_is_spam"  # The URL parameter name

    def lookups(self, request, model_admin):
        # Return the filter options as a list of tuples
        return Letter.SPAM

    def queryset(self, request, queryset):
        # Apply the filter to the queryset based on the selected option
        if self.value():
            return queryset.filter(letter__is_spam=self.value())
        return queryset


class AttachmentVirusScanListFilter(admin.SimpleListFilter):
    title = _("Virus Scan status")  # Displayed in the admin sidebar
    parameter_name = "virus_scan_status"  # The URL parameter name

    def lookups(self, request, model_admin):
        # Return the filter options as a list of tuples
        return Request.STATUS

    def queryset(self, request, queryset):
        # Define the content_type for Attachment
        attachment_ct = ContentType.objects.get_for_model(Attachment)

        if self.value() is not None:
            # Use a subquery to filter Attachments based on their related Request status
            queryset = queryset.filter(
                pk__in=Request.objects.filter(
                    content_type=attachment_ct,
                    object_id=OuterRef("pk"),
                    status=self.value(),
                ).values("object_id")
            )
        return queryset


class AttachmentVirusScanExistsFilter(admin.SimpleListFilter):
    title = _("Has Virus Scan Request")  # Displayed in the admin sidebar
    parameter_name = "virus_scan_exists"  # The URL parameter name

    def lookups(self, request, model_admin):
        return (
            ("True", _("Has scan request")),
            ("False", _("No scan request")),
        )

    def queryset(self, request, queryset):
        # Define the content_type for Attachment
        attachment_ct = ContentType.objects.get_for_model(Attachment)

        if self.value() == "True":
            # Find Attachments that have at least one related ScanRequest
            queryset = queryset.filter(
                pk__in=Request.objects.filter(
                    content_type=attachment_ct, object_id=OuterRef("pk")
                ).values("object_id")
            )

        elif self.value() == "False":
            # Find Attachments that have no related ScanRequest
            queryset = queryset.exclude(
                pk__in=Request.objects.filter(
                    content_type=attachment_ct, object_id=OuterRef("pk")
                ).values("object_id")
            )

        return queryset


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """
    Admin View for Attachment
    """

    list_display = (
        "id",
        "get_letter_id",
        "get_letter_is_spam",
        "attachment",
        "get_scan_status",
    )
    search_fields = (
        "id",
        "attachment",
        "letter__id",
    )
    list_filter = (
        AttachmentLetterSpamFilter,
        AttachmentVirusScanExistsFilter,
        AttachmentVirusScanListFilter,
    )
    ordering = ("-id",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        """
        Override the default get_queryset method to annotate the queryset with
        the latest scan_status from the related Request model.
        """
        queryset = super().get_queryset(request)

        # Define the content_type for Attachment
        attachment_ct = ContentType.objects.get_for_model(Attachment)

        # Add an annotation that gets the latest scan_status from the related Request
        latest_status_subquery = (
            Request.objects.filter(content_type=attachment_ct, object_id=OuterRef("pk"))
            .order_by("-created")
            .values("status")[:1]
        )  # Get the latest status

        return queryset.annotate(
            scan_status=Subquery(latest_status_subquery, output_field=IntegerField())
        )

    @admin.display(description=_("Virus Scan status"))
    def get_scan_status(self, obj):
        # Access the annotated scan_status field directly
        scan_status = getattr(
            obj, "scan_status", None
        )  # Safe access in case annotation is missing
        if scan_status is not None and scan_status in Request.STATUS._display_map:
            return Request.STATUS._display_map[scan_status]
        return "-"

    @admin.display(description=_("Letter is spam"))
    def get_letter_is_spam(self, obj):
        return obj.letter.is_spam

    @admin.display(description=_("Letter id"))
    def get_letter_id(self, obj):
        if obj.letter:
            # Generate a link to the Letter admin change page
            url = reverse("admin:letters_letter_change", args=[obj.letter.id])
            return format_html('<a href="{}">{}</a>', url, obj.letter.id)
        return "-"


class ReputableTLDListFilter(admin.SimpleListFilter):
    title = "TLD"
    parameter_name = "tld"

    def lookups(self, request, model_admin):
        return [
            ("reputable", _("Reputable TLDs")),
            ("non_reputable", _("Non-reputable TLDs")),
        ]

    def queryset(self, request, queryset):
        tlds = ReputableLetterEmailTLD.objects.values_list("name", flat=True)
        q_object = Q()
        for tld in tlds:
            q_object |= Q(domain_name__iendswith=tld)
        if self.value() == "reputable":
            return queryset.filter(q_object)
        elif self.value() == "non_reputable":
            return queryset.exclude(q_object)


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
        ReputableTLDListFilter,
    )
    search_fields = ("domain_name",)
    ordering = ("-email_from_count",)
    list_editable = ("is_spammer_domain", "is_non_spammer_domain")


@admin.register(ReputableLetterEmailTLD)
class ReputableLetterEmailTLDAdmin(admin.ModelAdmin):
    """
    Admin View for ReputableLetterEmailTLD
    """

    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
