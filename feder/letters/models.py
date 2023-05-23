import logging
import uuid

from atom.models import AttachmentBase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.core.mail.message import make_msgid, EmailMultiAlternatives
from django.contrib.contenttypes.fields import GenericRelation
from django.template.loader import render_to_string
from django.urls import reverse
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from feder.institutions.models import Institution
from feder.records.models import AbstractRecord, AbstractRecordQuerySet, Record
from feder.main.exceptions import FederValueError
from feder.cases.models import Case
from .utils import (
    text_email_wrapper,
    html_email_wrapper,
    normalize_msg_id,
    html_to_text,
    is_formatted_html,
    text_to_html,
)
from ..virus_scan.models import Request as ScanRequest
from django.utils import timezone
from ..es_search.queries import more_like_this, find_document
from feder.cases.models import enforce_quarantined_queryset
from feder.main.utils import get_email_domain
from feder.domains.models import Domain
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


class LetterQuerySet(AbstractRecordQuerySet):
    def attachment_count(self):
        return self.annotate(attachment_count=models.Count("attachment"))

    def with_author(self):
        return self.select_related("author_user", "author_institution")

    def for_milestone(self):
        return self.with_attachment().with_author()

    def for_api(self):
        return self.for_milestone().select_related("emaillog")

    def is_draft(self):
        return self.filter(is_draft=True).is_outgoing()

    def is_outgoing(self):
        return self.filter(author_user__isnull=False)

    def is_incoming(self):
        return self.filter(author_user__isnull=True)

    def recent(self):
        return self.filter(created__gt=timezone.now() - timezone.timedelta(days=7))

    def with_feed_items(self):
        return (
            self.with_author()
            .select_related(
                "record__case__institution__jst", "record__case__monitoring"
            )
            .with_attachment()
        )

    def with_attachment(self):
        return self.prefetch_related("attachment_set").prefetch_related(
            "attachment_set__scan_request"
        )

    def exclude_spam(self):
        return self.exclude(is_spam=Letter.SPAM.spam)

    def filter_automatic(self):
        return self.filter(message_type__in=[i[0] for i in Letter.MESSAGE_TYPES_AUTO])

    def exclude_automatic(self):
        return self.exclude(message_type__in=[i[0] for i in Letter.MESSAGE_TYPES_AUTO])

    def for_user(self, user):
        if user.is_anonymous:
            return self.filter(
                record__case__is_quarantined=False,
                record__case__monitoring__is_public=True,
            )
        if user.is_superuser or user.is_authenticated:
            return self


class LetterManager(BaseManager.from_queryset(LetterQuerySet)):
    def get_queryset(self):
        return (
            super().get_queryset()
            # TODO use this filter in particular views only
            # .filter(is_spam__in=[Letter.SPAM.unknown, Letter.SPAM.non_spam])
        )


class Letter(AbstractRecord):
    SPAM = Choices(
        (0, "unknown", _("Unknown")),
        (1, "non_spam", _("Non-spam")),
        (2, "spam", _("Spam")),
        (3, "probable_spam", _("Probable spam")),
    )
    MESSAGE_TYPES = Choices(
        (0, "unknown", _("Unknown")),
        (1, "regular", _("Regular")),
        (2, "disposition_notification", _("Disposition notification")),
        (3, "vacation_reply", _("Vacation reply")),
        (4, "mass_draft", _("Mass message draft")),
    )
    MESSAGE_TYPES_AUTO = MESSAGE_TYPES.subset(
        "disposition_notification", "vacation_reply"
    )

    author_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Author (if user)"),
        null=True,
        blank=True,
    )
    author_institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        verbose_name=_("Author (if institution)"),
        null=True,
        blank=True,
    )
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    body = models.TextField(verbose_name=_("Text"))
    html_body = models.TextField(verbose_name=_("Text in HTML"), blank=True)
    quote = models.TextField(verbose_name=_("Quote"), blank=True)
    html_quote = models.TextField(verbose_name=_("Quote in HTML"), blank=True)
    email = models.EmailField(verbose_name=_("E-mail"), max_length=100, blank=True)
    email_from = models.EmailField(
        verbose_name=_("From email address"), max_length=100, blank=True, null=True
    )
    email_to = models.EmailField(
        verbose_name=_("To email address"), max_length=100, blank=True, null=True
    )
    note = models.TextField(verbose_name=_("Comments from editor"), blank=True)
    is_spam = models.IntegerField(
        verbose_name=_("Is SPAM?"), choices=SPAM, default=SPAM.unknown, db_index=True
    )
    is_draft = models.BooleanField(verbose_name=_("Is draft?"), default=True)
    message_type = models.IntegerField(
        verbose_name=_("Message type"),
        choices=MESSAGE_TYPES,
        default=MESSAGE_TYPES.unknown,
    )
    mark_spam_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Spam marker"),
        help_text=_("The person who marked it as spam"),
        related_name="letter_mark_spam_by",
    )
    mark_spam_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Time of mark as spam"),
        help_text=_("Time when letter was marked as spam"),
    )
    message_id_header = models.CharField(
        blank=True,
        verbose_name=_('ID of sent email message "Message-ID"'),
        max_length=500,
    )
    eml = models.FileField(
        upload_to="messages/%Y/%m/%d", verbose_name=_("File"), null=True, blank=True
    )
    objects = LetterManager()
    objects_with_spam = LetterQuerySet.as_manager()

    def is_spam_validated(self):
        return self.is_spam != Letter.SPAM.unknown

    def is_mass_draft(self):
        return self.is_draft and self.message_type == self.MESSAGE_TYPES.mass_draft

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")
        ordering = ["created"]
        indexes = AbstractRecord.Meta.indexes
        permissions = (
            ("can_filter_eml", _("Can filter eml")),
            ("recognize_letter", _("Can recognize letter")),
        )

    def delete(self, *args, **kwargs):
        self.record.delete()  # Delete the associated Record instance
        super().delete(*args, **kwargs)

    @property
    def is_incoming(self):
        return not bool(self.author_user_id)

    @property
    def is_outgoing(self):
        return bool(self.author_user_id)

    def get_title(self):
        if self.title and self.title.strip():
            return self.title
        return _("(no subject)")

    def __str__(self):
        return force_str(self.get_title())

    def get_absolute_url(self):
        if self.case or self.is_mass_draft():
            url = reverse("letters:details", kwargs={"pk": self.pk})
        else:
            url = reverse("letters:assign", kwargs={"pk": self.pk})
        return url

    def get_eml_url(self):
        if not self.eml:
            return None
        return reverse("letters:download", kwargs={"pk": self.pk})

    @property
    def author(self):
        return self.author_user if self.author_user_id else self.author_institution

    @author.setter
    def author(self, value):
        if isinstance(value, Institution):
            self.author_user = None
            self.author_institution = value
        elif isinstance(value, get_user_model()):
            self.author_institution = None
            self.author_user = value
        else:
            raise ValueError(
                "Only User and Institution is allowed for attribute author"
            )

    @classmethod
    def send_new_case(cls, case):
        letter = cls(
            author_user=case.user,
            record=Record.objects.create(case=case),
            title=case.monitoring.subject,
            html_body=(
                case.monitoring.template
                if is_formatted_html(case.monitoring.template)
                else text_to_html(case.monitoring.template)
            ),
            body=(
                html_to_text(case.monitoring.template)
                if is_formatted_html(case.monitoring.template)
                else case.monitoring.template
            ),
        )
        letter.send(commit=True, only_email=False)
        return letter

    def _email_context(self):
        body = self.body.replace("{{EMAIL}}", self.case.email)
        html_body = self.html_body.replace("{{EMAIL}}", self.case.email)
        return {
            "html_body": mark_safe(html_body),
            "text_body": mark_safe(body),
            "html_footer": mark_safe(self.case.monitoring.email_footer),
            "text_footer": mark_safe(html_to_text(self.case.monitoring.email_footer)),
            "text_quote": mark_safe(text_email_wrapper(self.quote)),
            "html_quote": mark_safe(html_email_wrapper(self.html_quote)),
        }

    def html_body_with_footer(self):
        context = {
            "html_body": mark_safe(self.html_body),
            "html_footer": mark_safe(self.case.monitoring.email_footer),
        }
        return render_to_string("letters/_letter_reply_body.html", context)

    def email_body(self):
        context = self._email_context()
        html_content = render_to_string("letters/_letter_reply_body.html", context)
        txt_content = render_to_string("letters/_letter_reply_body.txt", context)
        return html_content, txt_content

    def _construct_message(self, msg_id=None):
        headers = {
            "Return-Receipt-To": self.case.email,
            "Disposition-Notification-To": self.case.email,
        }
        if msg_id:
            headers["Message-ID"] = msg_id
        html_content, txt_content = self.email_body()
        msg = EmailMultiAlternatives(
            subject=self.case.monitoring.subject,
            from_email=str(self.case.get_email_address()),
            reply_to=[self.case.email],
            to=[self.case.institution.email],
            body=txt_content,
            headers=headers,
            attachments=[
                (att.filename, att.attachment.file.read(), "application/octet-stream")
                for att in self.attachment_set.all()
            ],
        )
        msg.attach_alternative(html_content, "text/html")
        return msg

    def generate_mass_letters(self):
        """
        Uses this letter as a template for generating mass message
         (it has to be defined with "mass draft" message type).
         prepares and returns generated letters ready for sending.
        """
        if not self.is_mass_draft():
            raise FederValueError(
                'mass_send method can only be executed for "mass_draft" message type.'
            )

        # preparing letter content
        letter_data = {}
        for name in [
            "author_user",
            "title",
            "html_body",
            "html_quote",
            "body",
            "quote",
            "note",
        ]:
            letter_data[name] = getattr(self, name)
        letter_data["is_draft"] = False
        letter_data["message_type"] = self.MESSAGE_TYPES.regular

        letters = []
        for case in self.mass_draft.determine_cases():
            letter = Letter(**letter_data)
            letter.record = Record.objects.create(case=case)
            letter.save()

            # Copying attachments
            for attachment in self.attachment_set.all():
                attachment_copy = Attachment(letter=letter)
                file_copy = ContentFile(attachment.attachment.read())
                file_copy.name = attachment.attachment.name
                attachment_copy.attachment = file_copy
                attachment_copy.save()

            letters.append(letter)

        return letters

    def send(self, commit=True, only_email=False):
        if self.is_mass_draft():
            raise FederValueError(
                'send method can not be executed for "mass_draft" message type.'
            )
        self.case.update_email()
        msg_id = make_msgid(domain=self.case.email.split("@", 2)[1])
        message = self._construct_message(msg_id=msg_id)
        text = message.message().as_bytes()
        self.email = self.case.institution.email
        self.message_id_header = normalize_msg_id(msg_id)
        self.eml.save("%s.eml" % uuid.uuid4(), ContentFile(text), save=False)
        self.is_draft = False
        if commit:
            self.save(update_fields=["eml", "email"] if only_email else None)
        return message.send()

    def get_more_like_this(self):
        doc = find_document(self.pk)
        if not doc:
            return Letter._default_manager.none()
        result = more_like_this(doc)
        ids = [x.letter_id for x in result]
        return Letter._default_manager.filter(pk__in=ids).all()

    def spam_check(self):
        if self.email_from is not None and "@" in self.email_from:
            from_domain = LetterEmailDomain.objects.filter(
                domain_name=get_email_domain(self.email_from)
            ).first()
        else:
            from_domain = None
        if (
            # (self.email_to not in self.body) or
            (self.email_from is None or self.email_from == "")
            or (from_domain is not None and from_domain.is_spammer_domain)
        ):
            self.is_spam = Letter.SPAM.probable_spam
            self.save()
            return


class LetterEmailDomain(TimeStampedModel):
    domain_name = models.CharField(
        verbose_name=_("Email address domain"), max_length=100, blank=True, null=True
    )
    is_trusted_domain = models.BooleanField(
        verbose_name=_("Is trusted (own or partner) domain?"), default=False
    )
    is_monitoring_email_to_domain = models.BooleanField(
        verbose_name=_("Is monitoring Email To domain?"), default=False
    )
    is_spammer_domain = models.BooleanField(
        verbose_name=_("Is spammer domain?"), default=False
    )
    is_non_spammer_domain = models.BooleanField(
        verbose_name=_("Is non spammer domain?"), default=False
    )
    email_to_count = models.IntegerField(
        verbose_name=_("Email To addres counter"), default=0
    )
    email_from_count = models.IntegerField(
        verbose_name=_("Email From addres counter"), default=0
    )

    def save(self, *args, **kwargs):
        if (
            self.is_monitoring_email_to_domain
            or self.is_trusted_domain
            or self.is_non_spammer_domain
        ):
            self.is_spammer_domain = False
        super().save(*args, **kwargs)

    def add_email_to_letter(self):
        self.email_to_count += 1
        self.save()

    def add_email_from_letter(self):
        self.email_from_count += 1
        self.save()

    @classmethod
    def register_letter_email_domains(cls, letter: Letter):
        trusted_domains = Domain.objects.all().values_list("name", flat=True)
        is_outgoing = (
            letter.is_outgoing or "fedrowanie.siecobywatelska.pl" in letter.email_from
        )
        from_domain_name = get_email_domain(letter.email_from)
        from_domain, _ = cls.objects.get_or_create(domain_name=from_domain_name)
        from_domain.is_trusted_domain = from_domain.domain_name in trusted_domains
        from_domain.save()
        from_domain.add_email_from_letter()
        to_domain_name = get_email_domain(letter.email_to)
        to_domain, _ = cls.objects.get_or_create(domain_name=to_domain_name)
        to_domain.is_trusted_domain = to_domain.domain_name in trusted_domains
        to_domain.is_monitoring_email_to_domain = is_outgoing
        to_domain.save()
        to_domain.add_email_to_letter()


class MassMessageDraft(TimeStampedModel):
    letter = models.OneToOneField(
        to=Letter,
        verbose_name=_("Letter"),
        related_name="mass_draft",
        on_delete=models.CASCADE,
    )
    monitoring = models.ForeignKey(
        to="monitorings.Monitoring",
        verbose_name=_("Monitoring"),
        on_delete=models.CASCADE,
    )
    recipients_tags = models.ManyToManyField(
        to="cases_tags.Tag",
        verbose_name=_("Recipient tags"),
        help_text=_("Used to determine recipients by case tags."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Mass message draft")
        verbose_name_plural = _("Mass message drafts")

    def __str__(self):
        return f"Mass draft for {self.letter}"

    def determine_cases(self):
        return Case.objects.filter(
            monitoring=self.monitoring, tags__in=self.recipients_tags.all()
        )


class AttachmentQuerySet(models.QuerySet):
    def _enforce_quarantine(self, user):
        return enforce_quarantined_queryset(self, user, "letter__record__case")

    def for_user(self, user):
        if not user.is_superuser:
            return self.filter(
                letter__is_spam__in=[Letter.SPAM.unknown, Letter.SPAM.non_spam]
            )._enforce_quarantine(user)
        return self

    def with_scan_result(self):
        return self.prefetch_related("scan_request")


class Attachment(AttachmentBase):
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    objects = AttachmentQuerySet.as_manager()
    scan_request = GenericRelation(ScanRequest, verbose_name=_("Virus scan request"))

    def current_scan_request(self):
        scans = self.scan_request.all()
        if scans:
            return scans[0]

    def scan_status(self):
        scan = self.current_scan_request()
        if scan:
            return scan.status

    def is_infected(self):
        scan = self.scan_status()
        return scan == ScanRequest.STATUS.infected

    def __str__(self):
        if self.attachment:
            return f"{self.filename}"
        return "None"

    def get_absolute_url(self):
        return reverse(
            "letters:attachment", kwargs={"pk": self.pk, "letter_pk": self.letter_id}
        )

    def get_full_url(self):
        return "".join(
            ["https://", get_current_site(None).domain, self.get_absolute_url()]
        )
