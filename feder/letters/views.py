import json
import logging
import uuid
from os import path

from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import (
    ActionMessageMixin,
    ActionView,
    CreateMessageMixin,
    DeleteMessageMixin,
    UpdateMessageMixin,
)
from braces.views import (
    FormValidMessageMixin,
    MessageMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from cached_property import cached_property
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView
from django_filters.views import FilterView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView
from guardian.shortcuts import get_anonymous_user

from feder.alerts.models import Alert
from feder.cases.models import Case
from feder.letters.formsets import AttachmentInline
from feder.letters.settings import LETTER_RECEIVE_SECRET
from feder.llm_evaluation.tasks import categorize_letter_in_background
from feder.main.mixins import (
    AttrPermissionRequiredMixin,
    BaseXSendFileView,
    RaisePermissionRequiredMixin,
)
from feder.main.utils import DeleteViewLogEntryMixin
from feder.monitorings.models import Monitoring
from feder.monitorings.tasks import send_mass_draft
from feder.records.models import Record
from feder.virus_scan.models import Request as ScanRequest

from .filters import LetterFilter
from .forms import AssignLetterForm, LetterForm, ReplyForm
from .logs.tasks import update_sent_letter_status
from .mixins import LetterObjectFeedMixin, LetterSummaryTableMixin
from .models import Attachment, Letter, LetterEmailDomain
from .tasks import update_letter_attachments_text_content

_("Letters index")

logger = logging.getLogger(__file__)


class MixinGzipXSendFile:
    def get_sendfile_kwargs(self, context):
        kwargs = super().get_sendfile_kwargs(context)
        if kwargs["filename"] and kwargs["filename"].endswith(".gz"):
            kwargs["encoding"] = "gzip"
            filename = path.basename(kwargs["filename"][: -len(".gz")])
            kwargs["attachment_filename"] = filename
        return kwargs


class CaseRequiredMixin:
    def get_queryset(self):
        qs = super().get_queryset().exclude(record__case=None)
        return qs.attachment_count()


class LetterCommonMixin:
    """
    Defines get_queryset and get_permission_object methods.
    It should to be specified before permission related mixins.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(
                Q(record__case__isnull=True)
                & ~Q(message_type=Letter.MESSAGE_TYPES.mass_draft)
            )
            .attachment_count()
            .with_attachment()
        )

    def get_permission_object(self):
        obj = super().get_object()
        return (
            obj.mass_draft.monitoring
            if obj.is_mass_draft()
            else obj.record.case.monitoring
        )


class LetterListView(
    LetterCommonMixin,
    UserKwargFilterSetMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    LetterSummaryTableMixin,
    FilterView,
):
    filterset_class = LetterFilter
    model = Letter
    select_related = ["record__case"]
    prefetch_related = [
        "author_user",
        "author_institution",
        "record__case__institution",
    ]
    paginate_by = 25
    ordering = "-pk"

    def get_queryset(self):
        qs = super().get_queryset().exclude_spam()
        return qs.attachment_count().for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary_table"] = self.render_summary_table()
        return context


class LetterDetailView(SelectRelatedMixin, LetterCommonMixin, DetailView):
    model = Letter
    select_related = ["author_institution", "author_user", "record__case__monitoring"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["enable_refresh_attachment_text_content"] = True
        return context

    def get_queryset(self):
        qs = super().get_queryset().exclude_spam()
        return qs.for_user(self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "refresh_attachment_text_content" in request.POST:
            update_letter_attachments_text_content(
                self.object.pk, schedule=60, remove_existing_tasks=True
            )
            categorize_letter_in_background(
                self.object.pk, schedule=120, remove_existing_tasks=True
            )
            messages.success(
                request,
                _(
                    "Tasks to refresh letter attachements text content and categorize"
                    + " letter generated. It may take a while to get full update"
                    + " - check task queue in admin panel."
                ),
            )
        return self.get(request, *args, **kwargs)


class LetterMessageXSendFileView(MixinGzipXSendFile, BaseXSendFileView):
    model = Letter
    file_field = "eml"
    send_as_attachment = True

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.for_user(self.request.user).exclude_spam()


class LetterCreateView(
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    CreateMessageMixin,
    FormValidMessageMixin,
    CreateView,
):
    model = Letter
    form_class = LetterForm
    permission_required = "monitorings.add_letter"

    @cached_property
    def case(self):
        qs = Case.objects.select_related("monitoring").for_user(self.request.user)
        return get_object_or_404(qs, pk=self.kwargs["case_pk"])

    def get_permission_object(self):
        return self.case.monitoring

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["case"] = self.case
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.case
        context["monitoring"] = self.case.monitoring
        context["user"] = self.request.user
        return context


class LetterReplyView(
    LetterCommonMixin,
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    FormValidMessageMixin,
    CreateWithInlinesView,
):
    template_name = "letters/letter_reply.html"
    model = Letter
    form_class = ReplyForm
    inlines = [AttachmentInline]
    permission_required = "monitorings.add_draft"

    @cached_property
    def letter(self):
        return get_object_or_404(
            self.get_queryset()
            .select_related("record__case__monitoring")
            .for_user(self.request.user),
            pk=self.kwargs["pk"],
        )

    def get_permission_object(self):
        return self.letter.case.monitoring

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["letter"] = self.letter
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.letter
        context["reply"] = True
        return context

    def forms_valid(self, form, inlines):
        result = super().forms_valid(form, inlines)
        if "send" in self.request.POST:
            self.object.send()
            update_sent_letter_status(schedule=(3 * 60))
        return result

    def get_form_valid_message(self):
        if self.object.eml:
            return _("Reply {reply} to {letter} saved and send!").format(
                letter=self.letter, reply=self.object
            )
        return _("Reply {reply} to {letter} saved to review!").format(
            letter=self.letter, reply=self.object
        )


class LetterSendView(
    LetterCommonMixin, AttrPermissionRequiredMixin, MessageMixin, ActionView
):
    model = Letter
    permission_required = "monitorings.reply"
    template_name_suffix = "_send"

    def action(self):
        if self.object.is_mass_draft():
            cases_count = self.object.mass_draft.determine_cases().count()
            send_mass_draft(self.object.pk)
            self.messages.success(
                _(
                    'Message "{letter}" has been scheduled for sending '
                    "to {count} recipients!"
                ).format(letter=self.object, count=cases_count),
                fail_silently=True,
            )
        else:
            self.object.send()
            self.messages.success(
                _('Reply "{letter}" has been sent to {institution}!').format(
                    letter=self.object, institution=self.object.case.institution
                ),
                fail_silently=True,
            )
            update_sent_letter_status(schedule=(3 * 60))

    def get_success_url(self):
        if self.object.is_mass_draft():
            obj = self.object.mass_draft.monitoring
        else:
            obj = self.object
        return obj.get_absolute_url()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.for_user(self.request.user)


class LetterUpdateView(
    LetterCommonMixin,
    AttrPermissionRequiredMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    UpdateWithInlinesView,
):
    model = Letter
    form_class = LetterForm
    inlines = [AttachmentInline]
    permission_required = "monitorings.change_letter"

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user).with_attachment()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class LetterDeleteView(
    LetterCommonMixin,
    AttrPermissionRequiredMixin,
    DeleteMessageMixin,
    DeleteViewLogEntryMixin,
    DeleteView,
):
    model = Letter
    permission_required = "monitorings.delete_letter"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.for_user(self.request.user)

    def get_success_url(self):
        if self.object.is_mass_draft():
            url = self.object.mass_draft.monitoring.get_absolute_url()
        else:
            url = self.object.case.get_absolute_url()
        return url


class LetterRssFeed(Feed):
    title = _("Latest letters on whole site")
    link = reverse_lazy("letters:list")
    description = _(
        "Updates on new letters on site including "
        + "receving and sending in all monitorings."
    )
    feed_url = reverse_lazy("letters:rss")
    description_template = "letters/_letter_feed_item.html"

    def items(self):
        return (
            Letter.objects.with_feed_items()
            .exclude(record__case=None)
            .exclude_spam()
            .recent()
            .for_user(get_anonymous_user())
            .order_by("-created")[:30]
        )

    def item_title(self, item):
        return item.title

    def item_author_name(self, item):
        return force_str(item.author)

    def item_author_link(self, item):
        if item.author:
            return item.author.get_absolute_url()

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified

    def item_categories(self, item):
        return [
            item.case,
            item.case.monitoring,
            item.case.institution,
            item.case.institution.jst,
        ]

    def item_enclosure_url(self, item):
        return item.eml.url if item.eml else None


class LetterAtomFeed(LetterRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterMonitoringRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Monitoring
    filter_field = "record__case__monitoring"
    kwargs_name = "monitoring_pk"

    def title(self, obj):
        return _("Letter for monitoring %s") % force_str(obj)

    def description(self, obj):
        return _(
            "Archive of letter for cases which involved in monitoring %s"
        ) % force_str(obj)


class LetterMonitoringAtomFeed(LetterMonitoringRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterMonitoringRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterCaseRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Case
    filter_field = "record__case"
    kwargs_name = "case_pk"

    def title(self, obj):
        return _("Letter for case %s") % force_str(obj)

    def description(self, obj):
        return _("Archive of letter for case %s") % force_str(obj)


class LetterCaseAtomFeed(LetterCaseRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterCaseRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterReportSpamView(ActionMessageMixin, CaseRequiredMixin, ActionView):
    template_name_suffix = "_spam"
    model = Letter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_spam__in=[Letter.SPAM.unknown, Letter.SPAM.probable_spam])
            .for_user(self.request.user)
        )

    def action(self):
        author = None if self.request.user.is_anonymous else self.request.user
        Alert.objects.create(
            monitoring=self.object.case.monitoring,
            reason=_("SPAM"),
            author=author,
            link_object=self.object,
        )

    def get_success_message(self):
        return _(
            "Thanks for your help. The report was forwarded to responsible persons."
        )

    def get_success_url(self):
        return self.object.case.get_absolute_url()


class LetterResendView(
    ActionMessageMixin, AttrPermissionRequiredMixin, CaseRequiredMixin, ActionView
):
    template_name_suffix = "_resend"
    model = Letter
    permission_required = "monitorings.reply"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("record__case__monitoring")
            .is_outgoing()
            .for_user(self.request.user)
        )

    def get_permission_object(self):
        return self.get_object().case.monitoring

    def action(self):
        case = self.object.case
        self.resend = Letter(
            author_user=self.request.user,
            record=Record.objects.create(case=case),
            title=self.object.title,
            body=self.object.body,
            html_body=self.object.html_body,
        )
        self.resend.save()
        self.resend.send(commit=True, only_email=False)
        update_sent_letter_status(schedule=(3 * 60))

    def get_success_message(self):
        return _("The message was resend.")

    def get_success_url(self):
        return self.object.case.get_absolute_url()


class LetterMarkSpamView(RaisePermissionRequiredMixin, ActionMessageMixin, ActionView):
    template_name_suffix = "_mark_spam"
    model = Letter
    permission_required = "monitorings.spam_mark"
    accept_global_perms = True

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "object"):
            self.object = super().get_object(*args, **kwargs)
        return self.object

    def get_permission_object(self):
        if self.get_object().case:
            return self.get_object().case.monitoring
        return None

    def get_queryset(self):
        return (
            super().get_queryset()
            # .filter(is_spam__in=[Letter.SPAM.unknown, Letter.SPAM.probable_spam])
            .for_user(self.request.user)
        )

    def action(self):
        if "valid" in self.request.POST:
            self.object.is_spam = Letter.SPAM.non_spam
        else:
            self.object.is_spam = Letter.SPAM.spam
        self.object.mark_spam_by = self.request.user
        self.object.mark_spam_at = timezone.now()
        self.object.save(update_fields=["is_spam", "mark_spam_by", "mark_spam_at"])
        Alert.objects.link_object(self.object).update(
            solver=self.request.user, status=True
        )

    def get_success_message(self):
        if "valid" in self.request.POST:
            return _("The letter {object} has been marked as valid.").format(
                object=self.object
            )
        return _("The message {object} has been marked as spam and hidden.").format(
            object=self.object
        )

    def get_success_url(self):
        if self.get_object().case:
            return self.object.case.get_absolute_url()
        return reverse_lazy("letters:unrecognized_list")


class UnrecognizedLetterListView(
    UserKwargFilterSetMixin,
    RaisePermissionRequiredMixin,
    PrefetchRelatedMixin,
    LetterSummaryTableMixin,
    FilterView,
):
    filterset_class = LetterFilter
    model = Letter
    paginate_by = 10
    permission_object = None
    permission_required = "letters.recognize_letter"
    template_name_suffix = "_unrecognized_list"
    select_related = ["record"]
    prefetch_related = ["attachment_set"]
    ordering = "-pk"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(record__case=None)
            .exclude(message_type=Letter.MESSAGE_TYPES.mass_draft)
            .exclude_spam()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.update_object_list(context["object_list"])
        context["summary_table"] = self.render_summary_table()
        return context

    def update_object_list(self, object_list):
        result = []
        for obj in object_list:
            obj.assign_form = AssignLetterForm(letter=obj)
            result.append(obj)
        return result


class AssignLetterFormView(
    PrefetchRelatedMixin,
    RaisePermissionRequiredMixin,
    SuccessMessageMixin,
    FormView,
):
    model = Letter
    form_class = AssignLetterForm
    permission_object = None
    success_url = reverse_lazy("letters:unrecognized_list")
    permission_required = "letters.recognize_letter"
    template_name = "letters/letter_assign.html"
    success_message = _("Assigned letter to case '%(case)s'")

    @cached_property
    def letter(self):
        obj = get_object_or_404(self.model, pk=self.kwargs["pk"])
        obj.assign_form = self.form_class(letter=obj)
        return obj

    def get_context_data(self, **kwargs):
        kwargs["object"] = self.letter
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["letter"] = self.letter
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.save()
        output = super().form_valid(form)
        categorize_letter_in_background(self.letter.pk)
        return output

    def get_success_url(self):
        query_params = self.request.GET.copy()
        query_string = query_params.urlencode()
        success_url = reverse_lazy("letters:unrecognized_list") + "?" + query_string
        return success_url


class AttachmentXSendFileView(MixinGzipXSendFile, BaseXSendFileView):
    model = Attachment
    file_field = "attachment"
    send_as_attachment = True

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)

    def get_sendfile_kwargs(self, context):
        kwargs = super().get_sendfile_kwargs(context)
        if kwargs["filename"].endswith(".gz"):
            kwargs["encoding"] = "gzip"
        return kwargs

    def render_to_response(self, context):
        if context["object"].is_infected():
            raise PermissionDenied(
                _(
                    "You do not have permission to view that file. "
                    + "The file was considered dangerous."
                )
            )
        if not self.request.user.is_authenticated:
            raise PermissionDenied(_("You do not have permission to view that file."))
        if self.request.user.is_authenticated and not (
            self.request.user.is_superuser or self.request.user.can_download_attachment
        ):
            raise PermissionDenied(_("You do not have permission to view that file."))
        return super().render_to_response(context)


class AttachmentRequestCreateView(ActionMessageMixin, ActionView):
    template_name_suffix = "_request_scan"
    model = Attachment

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "object"):
            self.object = super().get_object(*args, **kwargs)
        return self.object

    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)

    def action(self):
        ScanRequest.objects.create(
            content_object=self.object,
            field_name="attachment",
        )

    def get_success_message(self):
        return _("The file {} has been queued for scanning").format(self.object)

    def get_success_url(self):
        return self.object.letter.get_absolute_url()


class ReceiveEmail(View):
    required_content_type = "multipart/form-data"
    required_version = "v2"

    def post(self, request):
        logger.info(f"Add letter POST request received: {request}")
        if request.GET.get("secret") != LETTER_RECEIVE_SECRET:
            logger.error("POST request permission denied")
            raise PermissionDenied
        if request.content_type != self.required_content_type:
            logger.error("The request has an invalid Content-Type. ")
            return HttpResponseBadRequest(
                "The request has an invalid Content-Type. "
                'The acceptable Content-Type is "{}".'.format(
                    self.required_content_type
                )
            )

        manifest = json.load(request.FILES["manifest"])

        if manifest.get("version") != self.required_version:
            logger.error("The request has an invalid format version. ")
            return HttpResponseBadRequest(
                "The request has an invalid format version. "
                'The acceptable format version is "{}".'.format(self.required_version)
            )

        eml_data = request.FILES["eml"]
        logger.info(f'Letter to add: {manifest["headers"]}')
        letter = self.get_letter(
            headers=manifest["headers"],
            eml_manifest=manifest["eml"],
            text=manifest["text"],
            eml_data=eml_data,
        )
        LetterEmailDomain.register_letter_email_domains(letter=letter)
        letter_attachemnts = Attachment.objects.bulk_create(
            self.get_attachment(attachment, letter)
            for attachment in request.FILES.getlist("attachment")
        )
        letter.save()
        logging.info(f"Letter attachments created: {letter_attachemnts}")
        update_letter_attachments_text_content(letter.pk)
        categorize_letter_in_background(letter.pk)
        return JsonResponse({"status": "OK", "letter": letter.pk})

    def get_letter(self, headers, eml_manifest, text, eml_data, **kwargs):
        case = self.get_case(headers["to+"])
        eml_file = self.get_eml_file(eml_manifest, eml_data)
        from_email = headers["from"][0] if headers["from"][0] else "unknown@domain.gov"

        auto_reply = headers.get("auto_reply_type")
        if auto_reply is not None:
            auto_reply = auto_reply.replace("-", "_")
            message_type = getattr(
                Letter.MESSAGE_TYPES, auto_reply, Letter.MESSAGE_TYPES.unknown
            )
        else:
            message_type = Letter.MESSAGE_TYPES.regular

        if Letter.objects.filter(
            email_from=headers["from"][0] if headers.get("from") else None,
            email_to=headers["to"][0] if headers.get("to") else None,
            message_id_header=headers["message_id"],
            title=headers["subject"],
        ).exists():
            letter_to_add = Letter.objects.filter(
                email_from=headers["from"][0] if headers.get("from") else None,
                email_to=headers["to"][0] if headers.get("to") else None,
                message_id_header=headers["message_id"],
                title=headers["subject"],
            ).first()
            letter_to_add.spam_check()
            logger.info(f"Request skipped, letter exists: {letter_to_add.pk}")
            return letter_to_add

        letter_to_add = Letter.objects.create(
            author_institution=case.institution if case else None,
            email=from_email,
            email_from=headers["from"][0] if headers.get("from") else None,
            email_to=headers["to"][0] if headers.get("to") else None,
            message_id_header=headers["message_id"],
            record=Record.objects.create(case=case),
            message_type=message_type,
            title=headers["subject"],
            body=text["content"],
            html_body=text.get("html_content", ""),
            quote=text["quote"],
            html_quote=text.get("html_quote", ""),
            eml=eml_file,
            is_draft=False,
        )
        letter_to_add.spam_check()
        logger.info(f"Request processed, letter added: {letter_to_add.pk}")
        return letter_to_add

    def get_case(self, to_plus):
        return Case.objects.select_related("institution").by_addresses(to_plus).first()

    def get_attachment(self, attachment, letter):
        file_obj = ContentFile(content=attachment.read(), name=attachment.name)
        return Attachment(letter=letter, attachment=file_obj)

    def get_eml_file(self, eml_manifest, eml_data):
        eml_extensions = "eml.gz" if eml_manifest["compressed"] else "eml"
        eml_filename = f"{uuid.uuid4().hex}.{eml_extensions}"
        eml_content = eml_data.read()
        return ContentFile(eml_content, eml_filename)
