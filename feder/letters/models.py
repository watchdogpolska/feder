import email
import gzip
import json
import logging
import uuid
from email.utils import getaddresses

import requests
from atom.models import AttachmentBase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.mail.message import EmailMultiAlternatives, make_msgid
from django.core.validators import validate_email
from django.db import models
from django.db.models.manager import BaseManager
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField
from model_utils import Choices

from feder.cases.models import Case, enforce_quarantined_queryset
from feder.domains.models import Domain
from feder.institutions.models import Institution
from feder.llm_evaluation.prompts import (
    NORMALIZED_RESPONSE_ANSWER_CATEGORY_KEY,
    NORMALIZED_RESPONSE_ANSWER_KEY,
    NORMALIZED_RESPONSE_QUESTION_KEY,
    letter_categories_list,
    letter_categories_text,
)
from feder.main.exceptions import FederValueError
from feder.main.utils import get_email_domain, render_normalized_response_html_table
from feder.records.models import AbstractRecord, AbstractRecordQuerySet, Record

from ..virus_scan.models import Request as ScanRequest
from .logs.tasks import update_sent_letter_status
from .utils import (
    html_email_wrapper,
    html_to_text,
    is_formatted_html,
    normalize_msg_id,
    text_email_wrapper,
    text_to_html,
)

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
            ).exclude_spam()
        if user.is_superuser:
            return self
        return self.exclude_spam()


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
        on_delete=models.PROTECT,
        verbose_name=_("Author (if user)"),
        null=True,
        blank=True,
    )
    author_institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        verbose_name=_("Author (if institution)"),
        null=True,
        blank=True,
    )
    title = models.CharField(verbose_name=_("Subject"), max_length=200)
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
    ai_evaluation = models.TextField(
        verbose_name=_("Letter AI evaluation"), blank=True, null=True
    )
    normalized_response = JSONField(
        verbose_name=_("Normalized monitoring response"),
        null=True,
        blank=True,
    )
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
        on_delete=models.PROTECT,
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

    class Meta:
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")
        ordering = ["created"]
        indexes = AbstractRecord.Meta.indexes
        permissions = (
            ("can_filter_eml", _("Can filter eml")),
            ("recognize_letter", _("Can recognize letter")),
        )
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(author_user__isnull=False, author_institution__isnull=True)
                    | models.Q(
                        author_user__isnull=True, author_institution__isnull=False
                    )
                    | models.Q(
                        author_user__isnull=True, author_institution__isnull=True
                    )
                ),
                name="only_one_or_none_author",
            ),
        ]

    def is_spam_validated(self):
        return self.is_spam in (Letter.SPAM.spam, Letter.SPAM.non_spam)

    def is_mass_draft(self):
        return self.is_draft and self.message_type == self.MESSAGE_TYPES.mass_draft

    def delete(self, *args, **kwargs):
        self.record.delete()  # Delete the associated Record instance
        super().delete(*args, **kwargs)

    @property
    def is_delete_protected(self):
        return self.llmletterrequest_set.count() != 0

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
        context = {
            "html_body": mark_safe(
                case.monitoring.template
                if is_formatted_html(case.monitoring.template)
                else text_to_html(case.monitoring.template)
            ),
            "text_body": mark_safe(
                html_to_text(case.monitoring.template)
                if is_formatted_html(case.monitoring.template)
                else case.monitoring.template
            ),
            "html_footer": mark_safe(
                case.monitoring.email_footer
                if is_formatted_html(case.monitoring.email_footer)
                else text_to_html(case.monitoring.email_footer)
            ),
            "text_footer": mark_safe(
                html_to_text(case.monitoring.email_footer)
                if is_formatted_html(case.monitoring.email_footer)
                else case.monitoring.email_footer
            ),
        }
        letter = cls(
            author_user=case.user,
            email_from=str(case.get_email_address()),
            record=Record.objects.create(case=case),
            title=case.monitoring.subject,
            html_body=render_to_string("letters/_letter_reply_body.html", context),
            body=render_to_string("letters/_letter_reply_body.txt", context),
        )
        letter.save()
        letter.send(commit=True, only_email=False)
        update_sent_letter_status(schedule=(3 * 60))
        return letter

    def _email_context(self):
        body = self.body.replace("{{EMAIL}}", self.case.email).replace(
            "{{ADRESAT}}", self.case.institution.name
        )
        html_body = self.html_body.replace("{{EMAIL}}", self.case.email).replace(
            "{{ADRESAT}}", self.case.institution.name
        )
        quote = self.quote.replace("{{EMAIL}}", self.case.email).replace(
            "{{ADRESAT}}", self.case.institution.name
        )
        html_quote = self.html_quote.replace("{{EMAIL}}", self.case.email).replace(
            "{{ADRESAT}}", self.case.institution.name
        )
        context = {
            "html_body": mark_safe(html_body),
            "text_body": mark_safe(body),
            # "html_footer": mark_safe(self.case.monitoring.email_footer),
            # "text_footer": mark_safe(html_to_text(self.case.monitoring.email_footer)),
            "text_quote": mark_safe(text_email_wrapper(quote)),
            "html_quote": mark_safe(html_email_wrapper(html_quote)),
        }
        return context

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
            subject=(
                self.case.monitoring.subject if self.is_mass_draft() else self.title
            ),
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
            if self.case.first_request is None:
                self.case.first_request = self
                self.case.save()
            else:
                self.case.last_request = self
                self.case.save()
        return message.send()

    def get_recipients(self):
        """
        Returns a list of all email addresses from the "To" and "Cc" fields of the
        Letter eml file.
        """
        if not self.eml:
            if self.email_to:
                return [self.email_to]
            return []

        with self.eml.open(mode="rb") as f:
            # Check if the file is a gzip file by reading its magic number
            magic_number = f.read(2)
            f.seek(0)  # Reset file pointer to the beginning

            if magic_number == b"\x1f\x8b":
                with gzip.open(f, mode="rb") as gz:
                    msg = email.message_from_binary_file(gz)
            else:
                msg = email.message_from_binary_file(f)

        to_addrs = msg.get_all("To", [])
        cc_addrs = msg.get_all("Cc", [])

        all_addrs = to_addrs + cc_addrs

        return [addr for name, addr in getaddresses(all_addrs)]

    @property
    def allowed_recipient(self):
        """
        Returns True if any of the recipients from Letter.get_recipients email domain
        is in monitoring domains.
        """
        recipients = self.get_recipients()
        monitoring_domains = Domain.objects.all().values_list("name", flat=True)

        for recipient in recipients:
            try:
                validate_email(recipient)
                recipient_domain = recipient.split("@")[1]
                if recipient_domain in monitoring_domains:
                    return True
            except ValidationError:
                pass

        return False

    def spam_check(self):
        if not self.allowed_recipient:
            self.is_spam = Letter.SPAM.probable_spam
            self.save()
            return
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

    def get_full_content(self):
        attachments_text_content_list = [
            (
                attachment.text_content
                if attachment.text_content_update_result == "Processed"
                and attachment.text_content
                else ""
            )
            for attachment in self.attachment_set.all()
        ]
        attachments_text_content = "\n".join(attachments_text_content_list)
        return self.body + "\n" + attachments_text_content

    def ai_prompt_help(self):
        return (
            "Ocena wykonana za pomocą Azure OpenAI. Wszystkie możliwe opcje: \n\n"
            + letter_categories_text.format(
                institution=self.case.institution.name if self.case else "???"
            )
        )

    def ai_letter_category_choices(self):
        return list(
            (
                " ".join(
                    item.format(
                        institution=self.case.institution.name if self.case else "???"
                    )
                    .replace("\n", "")
                    .split()
                ),
                " ".join(
                    item.format(
                        institution=self.case.institution.name if self.case else "???"
                    )
                    .replace("\n", "")
                    .split()
                ),
            )
            for item in letter_categories_list
        )

    def get_normalized_response_html_table(self):
        if self.normalized_response:
            response_received = timezone.localtime(self.created).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            return mark_safe(
                f"<p> Otrzymano: {response_received} </p>"
                + render_normalized_response_html_table(self.normalized_response)
            )
        return ""

    def get_normalized_response_dict(self):
        try:
            return json.loads(self.normalized_response)
        except json.JSONDecodeError:
            return {}

    def get_normalized_question_and_answer_dict(self, question_number=None):
        response_dict = self.get_normalized_response_dict()
        if question_number in response_dict:
            return response_dict.get(question_number)
        return {
            NORMALIZED_RESPONSE_QUESTION_KEY: "",
            NORMALIZED_RESPONSE_ANSWER_KEY: "",
        }

    def set_normalized_answer_category(self, question_number, answer_category):
        response_dict = self.get_normalized_response_dict()
        response_dict[question_number][
            NORMALIZED_RESPONSE_ANSWER_CATEGORY_KEY
        ] = answer_category
        self.normalized_response = json.dumps(response_dict)
        self.save()

    @property
    def normalized_answer_created(self):
        if not self.normalized_response:
            return None

        from feder.llm_evaluation.models import LlmLetterRequest

        llm_request = (
            LlmLetterRequest.objects.filter(
                name="get_normalized_answers",
                evaluated_letter=self,
                status=LlmLetterRequest.STATUS.done,
            )
            .order_by("created")
            .last()
        )
        return llm_request.created if llm_request else None

    @property
    def normalized_answer_is_up_to_date(self):
        if (
            self.normalized_answer_created is not None
            and self.case.monitoring.normalized_response_template_created is not None
            and self.normalized_answer_created
            > self.case.monitoring.normalized_response_template_created
        ):
            if (
                self.case.monitoring.letter_normalization_prompt_extension_modified
                is not None
                and self.case.monitoring.letter_normalization_prompt_extension_modified
                > self.normalized_answer_created
            ):
                return False
            return True
        return False


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
        if letter.email_from and "@" in letter.email_from:
            from_domain_name = get_email_domain(letter.email_from)
            from_domain, _ = cls.objects.get_or_create(domain_name=from_domain_name)
            from_domain.is_trusted_domain = from_domain.domain_name in trusted_domains
            from_domain.save()
            from_domain.add_email_from_letter()
        if letter.email_to and "@" in letter.email_to:
            to_domain_name = get_email_domain(letter.email_to)
            to_domain, _ = cls.objects.get_or_create(domain_name=to_domain_name)
            to_domain.is_trusted_domain = to_domain.domain_name in trusted_domains
            to_domain.is_monitoring_email_to_domain = is_outgoing
            to_domain.save()
            to_domain.add_email_to_letter()

    class Meta:
        verbose_name = _("Letter Email domain")
        verbose_name_plural = _("Letter Email domains")


def validate_tld_name(value):
    if not value.isalpha():
        raise ValidationError(_("TLD name must be a single word"), code="invalid")


class ReputableLetterEmailTLD(TimeStampedModel):
    name = models.CharField(
        verbose_name=_("Email address repurable TLD"),
        max_length=100,
        blank=False,
        null=False,
        unique=True,
        validators=[validate_tld_name],
    )

    class Meta:
        verbose_name = _("Reputable Letter Email TLD")
        verbose_name_plural = _("Reputable Letter Email TLDs")


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
        on_delete=models.PROTECT,
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
        ).filter(institution__archival=False)


class AttachmentQuerySet(models.QuerySet):
    def _enforce_quarantine(self, user):
        return enforce_quarantined_queryset(self, user, "letter__record__case")

    def for_user(self, user):
        if not user.is_superuser:
            # Align attachment visibility with letter visibility
            # return self.exclude(letter__is_spam=Letter.SPAM.spam)._enforce_quarantine(
            #     user
            # )
            return self.filter(letter__in=Letter.objects.for_user(user))
        return self

    def with_scan_result(self):
        return self.prefetch_related("scan_request")


class Attachment(TimeStampedModel, AttachmentBase):
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    objects = AttachmentQuerySet.as_manager()
    scan_request = GenericRelation(ScanRequest, verbose_name=_("Virus scan request"))
    text_content = models.TextField(
        verbose_name=_("Text content"), blank=True, null=True
    )
    text_content_update_result = models.TextField(
        verbose_name=_("Text content update result"), blank=True, null=True
    )

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

    def update_text_content(self):
        try:
            logger.info(
                f"Updating text content for att. {self.pk}: {self.attachment.name}"
            )
            response = requests.post(
                settings.FILE_TO_TEXT_URL,
                files={
                    "file": (
                        self.attachment.name.split("/")[-1],
                        self.attachment.read(),
                    )
                },
                headers={"Authorization": f"JWT {settings.FILE_TO_TEXT_TOKEN}"},
            )
            if response.status_code != 200:
                msg = (
                    f"File to text API response: {response.status_code},"
                    + f" content: {response.content.decode('utf-8')}"
                )
                logger.error(msg)
                self.text_content_update_result = msg
                # save update_fields does not work with MySQL 5.7
                # self.save(update_fields=["text_content_update_result"])
                self.save()
                return False
            log_message_dict = response.json().copy()
            _ = log_message_dict.pop("text")
            logger.info(
                f"File to text API response:{response.status_code}, {log_message_dict}"
            )
            self.text_content = response.json()["text"]
            self.text_content_update_result = response.json()["message"]
            # save update_fields does not work with MySQL 5.7
            # self.save(update_fields=["text_content", "text_content_update_result"])
            self.save()
            return True
        except Exception as e:
            logger.error(e)
            self.text_content_update_result = str(e)
            # save update_fields does not work with MySQL 5.7
            # self.save(update_fields=["text_content_update_result"])
            self.save()
            return False

    @property
    def text_content_warning(self):
        warning = """
            Uwaga: treść załączników została odczytana maszynowo, więc może
            zawierać błędy związane z nieprawidłowym odczytaniem znaków,
            a także błędną interpretacji układu tekstu na stronie.
            Jeśli nie masz stosownych uprawnień i potrzebujesz dostępu
            do oryginału, skontaktuj się z biurem SOWP.

        """
        return warning  # " ".join(warning.split())
