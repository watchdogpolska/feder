import json
import uuid
from os import path
from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import (
    CreateMessageMixin,
    DeleteMessageMixin,
    UpdateMessageMixin,
    ActionView,
    ActionMessageMixin,
)
from braces.views import (
    FormValidMessageMixin,
    SelectRelatedMixin,
    PrefetchRelatedMixin,
    UserFormKwargsMixin,
)
from cached_property import cached_property
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.utils.encoding import force_text
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView
from django_filters.views import FilterView
from extra_views import UpdateWithInlinesView, CreateWithInlinesView

from feder.alerts.models import Alert
from feder.cases.models import Case
from feder.main.mixins import DisableOrderingListViewMixin, PerformantPagintorMixin
from feder.letters.formsets import AttachmentInline
from feder.letters.settings import LETTER_RECEIVE_SECRET
from feder.main.mixins import (
    AttrPermissionRequiredMixin,
    RaisePermissionRequiredMixin,
    BaseXSendFileView,
)
from feder.monitorings.models import Monitoring
from feder.records.models import Record
from .filters import LetterFilter
from .forms import LetterForm, ReplyForm, AssignLetterForm
from .mixins import LetterObjectFeedMixin
from .models import Letter, Attachment
from ..virus_scan.models import Request as ScanRequest

_("Letters index")


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


class LetterListView(
    UserKwargFilterSetMixin,
    DisableOrderingListViewMixin,
    CaseRequiredMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    PerformantPagintorMixin,
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

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.attachment_count()


class LetterDetailView(SelectRelatedMixin, CaseRequiredMixin, DetailView):
    model = Letter
    select_related = ["author_institution", "author_user", "record__case__monitoring"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.with_attachment()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.ELASTICSEARCH_SHOW_SIMILAR:
            context["similar_list"] = context["object"].get_more_like_this()
        context["show_similar"] = settings.ELASTICSEARCH_SHOW_SIMILAR
        return context


class LetterMessageXSendFileView(MixinGzipXSendFile, BaseXSendFileView):
    model = Letter
    file_field = "eml"
    send_as_attachment = True


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
        return get_object_or_404(
            Case.objects.select_related("monitoring"), pk=self.kwargs["case_pk"]
        )

    def get_permission_object(self):
        return self.case.monitoring

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["case"] = self.case
        return kw


class LetterReplyView(
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    FormValidMessageMixin,
    CaseRequiredMixin,
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
            Letter.objects.select_related("record__case__monitoring"),
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
        return context

    def forms_valid(self, form, inlines):
        result = super().forms_valid(form, inlines)
        if "send" in self.request.POST:
            self.object.send()
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
    AttrPermissionRequiredMixin, ActionMessageMixin, CaseRequiredMixin, ActionView
):
    model = Letter
    permission_attribute = "record__case__monitoring"
    permission_required = "monitorings.reply"
    template_name_suffix = "_send"

    def action(self):
        self.object.send()

    def get_success_message(self):
        return _("Reply {letter} send to {institution}!").format(
            letter=self.object, institution=self.object.case.institution
        )

    def get_success_url(self):
        return self.object.get_absolute_url()


class LetterUpdateView(
    AttrPermissionRequiredMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    CaseRequiredMixin,
    UpdateWithInlinesView,
):
    model = Letter
    form_class = LetterForm
    inlines = [AttachmentInline]
    permission_attribute = "record__case__monitoring"
    permission_required = "monitorings.change_letter"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.with_attachment()


class LetterDeleteView(
    AttrPermissionRequiredMixin, DeleteMessageMixin, CaseRequiredMixin, DeleteView
):
    model = Letter
    permission_attribute = "record__case__monitoring"
    permission_required = "monitorings.delete_letter"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        # Manually deleting related files
        for att_obj in obj.attachment_set.all():
            att_obj.attachment.delete()
        obj.eml.delete()
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.case.get_absolute_url()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.with_attachment()


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
            .recent()
            .order_by("-created")[:30]
        )

    def item_title(self, item):
        return item.title

    def item_author_name(self, item):
        return force_text(item.author)

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
        return _("Letter for monitoring %s") % force_text(obj)

    def description(self, obj):
        return _(
            "Archive of letter for cases which involved in monitoring %s"
        ) % force_text(obj)


class LetterMonitoringAtomFeed(LetterMonitoringRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterMonitoringRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterCaseRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Case
    filter_field = "record__case"
    kwargs_name = "case_pk"

    def title(self, obj):
        return _("Letter for case %s") % force_text(obj)

    def description(self, obj):
        return _("Archive of letter for case %s") % force_text(obj)


class LetterCaseAtomFeed(LetterCaseRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterCaseRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterReportSpamView(ActionMessageMixin, CaseRequiredMixin, ActionView):
    template_name_suffix = "_spam"
    model = Letter

    def get_queryset(self):
        return super().get_queryset().filter(is_spam=Letter.SPAM.unknown)

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


class LetterMarkSpamView(
    RaisePermissionRequiredMixin, CaseRequiredMixin, ActionMessageMixin, ActionView
):
    template_name_suffix = "_mark_spam"
    model = Letter
    permission_required = "monitorings.spam_mark"
    accept_global_perms = True

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "object"):
            self.object = super().get_object(*args, **kwargs)
        return self.object

    def get_permission_object(self):
        return self.get_object().case.monitoring

    def get_queryset(self):
        return super().get_queryset().filter(is_spam=Letter.SPAM.unknown)

    def action(self):
        if "valid" in self.request.POST:
            self.object.is_spam = Letter.SPAM.non_spam
        else:
            self.object.is_spam = Letter.SPAM.spam
        self.object.mark_spam_by = self.request.user
        self.object.mark_spam_at = datetime.now()
        self.object.save(update_fields=["is_spam", "mark_spam_by"])
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
        return self.object.case.get_absolute_url()


class UnrecognizedLetterListView(
    UserKwargFilterSetMixin,
    RaisePermissionRequiredMixin,
    PrefetchRelatedMixin,
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
        return super().get_queryset().filter(record__case=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.update_object_list(context["object_list"])
        return context

    def update_object_list(self, object_list):
        result = []
        for obj in object_list:
            obj.assign_form = AssignLetterForm(letter=obj)
            result.append(obj)
        return result


class AssignLetterFormView(
    PrefetchRelatedMixin, RaisePermissionRequiredMixin, SuccessMessageMixin, FormView
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
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


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
                "You do not have permission to view that file. "
                "The file was considered dangerous."
            )
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
        if request.GET.get("secret") != LETTER_RECEIVE_SECRET:
            raise PermissionDenied
        if request.content_type != self.required_content_type:
            return HttpResponseBadRequest(
                "The request has an invalid Content-Type. "
                'The acceptable Content-Type is "{}".'.format(
                    self.required_content_type
                )
            )

        manifest = json.load(request.FILES["manifest"])

        if manifest.get("version") != self.required_version:
            return HttpResponseBadRequest(
                "The request has an invalid format version. "
                'The acceptable format version is "{}".'.format(self.required_version)
            )

        eml_data = request.FILES["eml"]

        letter = self.get_letter(
            headers=manifest["headers"],
            eml_manifest=manifest["eml"],
            text=manifest["text"],
            eml_data=eml_data,
        )
        Attachment.objects.bulk_create(
            self.get_attachment(attachment, letter)
            for attachment in request.FILES.getlist("attachment")
        )
        return JsonResponse({"status": "OK", "letter": letter.pk})

    def get_letter(self, headers, eml_manifest, text, eml_data, **kwargs):
        case = self.get_case(headers["to+"])
        eml_file = self.get_eml_file(eml_manifest, eml_data)
        from_email = headers["from"][0] if headers["from"][0] else "unknown@domain.gov"
        message_type = Letter.MESSAGE_TYPES.get(
            headers["auto_reply_type"], Letter.MESSAGE_TYPES["regular"]
        )
        return Letter.objects.create(
            author_institution=case.institution if case else None,
            email=from_email,
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

    def get_case(self, to_plus):
        return Case.objects.select_related("institution").by_addresses(to_plus).first()

    def get_attachment(self, attachment, letter):
        file_obj = ContentFile(content=attachment.read(), name=attachment.name)
        return Attachment(letter=letter, attachment=file_obj)

    def get_eml_file(self, eml_manifest, eml_data):
        eml_extensions = "eml.gz" if eml_manifest["compressed"] else "eml"
        eml_filename = "{}.{}".format(uuid.uuid4().hex, eml_extensions)
        eml_content = eml_data.read()
        return ContentFile(eml_content, eml_filename)
