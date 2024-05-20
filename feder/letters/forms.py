from atom.ext.crispy_forms.forms import HelperMixin, SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Column, Fieldset, Layout, Row, Submit
from dal import autocomplete
from django import forms
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE

from feder.cases.models import Case
from feder.letters.utils import BODY_REPLY_TPL
from feder.llm_evaluation.tasks import (
    categorize_letter_in_background,
    update_letter_normalized_answers,
)
from feder.records.models import Record

from .models import Letter
from .utils import (
    HtmlIframeWidget,
    html_to_text,
    is_formatted_html,
    text_email_wrapper,
    text_to_html,
)

QUOTE_TPL = "W nawiązaniu do pisma z dnia {created} z adresu {email}:\n{quoted}"


class LetterForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    case = forms.ModelChoiceField(
        queryset=Case.objects.all(),
        label=_("Case"),
        widget=autocomplete.ModelSelect2(url="cases:autocomplete-find"),
    )
    ai_evaluation = forms.ChoiceField(
        choices=[],
        label=_("Letter AI evaluation"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        case = kwargs.pop("case", None)
        letter = kwargs.get("instance")
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if letter:
            self.fields["ai_evaluation"].choices = [
                (letter.ai_evaluation, letter.ai_evaluation)
            ] + letter.ai_letter_category_choices()
        if letter and letter.is_mass_draft():
            del self.fields["case"]
            del self.fields["ai_evaluation"]
        else:
            self.initial["case"] = case or letter.case
        self.helper.form_tag = False
        if not letter or letter.is_mass_draft() or letter.is_draft:
            self.fields["html_body"].widget = TinyMCE(
                attrs={
                    "cols": 80,
                    "rows": 20,
                },
            )
            self.fields["html_body"].initial = self.get_html_body_with_footer(case=case)
        else:
            self.initial["html_body"] = letter.html_body or text_to_html(letter.body)
            self.fields["html_body"].widget = HtmlIframeWidget(
                attrs={
                    "cols": 80,
                    "rows": 20,
                },
            )
            self.fields["html_body"].widget.attrs["readonly"] = True
            self.fields["html_body"].widget.label = self.fields["html_body"].label
            self.fields["title"].widget.attrs["readonly"] = True

    class Meta:
        model = Letter
        fields = ["title", "html_body", "case", "ai_evaluation", "note"]

    def get_html_body_with_footer(self, case=None):
        reply_info = BODY_REPLY_TPL.replace("\n", "")
        context = {
            "html_body": mark_safe(f"<p></p><p>{reply_info}</p>"),
            "html_footer": mark_safe(""),
        }
        if case:
            context["html_footer"] = mark_safe(case.monitoring.email_footer)
        return render_to_string("letters/_letter_reply_body.html", context)

    def save(self, *args, **kwargs):
        self.instance.body = html_to_text(self.cleaned_data["html_body"])
        if (
            not (
                self.fields["html_body"].widget.attrs["readonly"]
                or self.fields["title"].widget.attrs["readonly"]
            )
            and ("title" in self.changed_data or "html_body" in self.changed_data)
            and not self.instance.author_institution
        ):
            self.instance.author_user = self.user
        if not self.instance.is_mass_draft() and "ai_evaluation" in self.changed_data:
            update_letter_normalized_answers(self.instance.pk)
            messages.success(
                self.request,
                _(
                    "AI evaluation was changed."
                    + " Task to update letter normalized answers created"
                ),
            )
        if not self.instance.is_mass_draft() and "case" in self.changed_data:
            if hasattr(self.instance, "record"):
                self.instance.record.case = self.cleaned_data["case"]
            else:
                self.instance.record = Record.objects.create(
                    case=self.cleaned_data["case"]
                )
            self.instance.record.save()
            if "ai_evaluation" not in self.changed_data:
                categorize_letter_in_background(self.instance.pk)
                messages.success(
                    self.request,
                    _(
                        "Case was changed. Task to update letter"
                        + " categorization and upadte normalized answers created"
                    ),
                )
        self.instance.save()

        return super().save(*args, **kwargs)


class ReplyForm(HelperMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop("letter")
        super().__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.user_can_reply = self.user.has_perm("reply", self.letter.case.monitoring)
        self.user_can_save = self.user.has_perm(
            "add_draft", self.letter.case.monitoring
        )
        self.fields["html_body"].widget = TinyMCE(attrs={"cols": 80, "rows": 25})
        self.fields["html_quote"].widget = HtmlIframeWidget(
            attrs={"cols": 80, "rows": 10}
        )
        self.fields["note"].widget.attrs["rows"] = 6
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(_("Message"), "title", "html_body"),
                    css_class="form-group col-md-6 mb-0",
                ),
                Column(
                    Fieldset(_("Message continued"), "html_quote", "note"),
                    css_class="form-group col-md-6 mb-0",
                ),
            )
        )
        self.set_dynamic_field_initial()
        self.add_form_buttons()

    def get_html_body_with_footer(self):
        reply_info = BODY_REPLY_TPL.replace("\n", "")
        context = {
            "html_body": mark_safe(f"<p></p><p>{reply_info}</p>"),
            "html_footer": mark_safe(self.letter.case.monitoring.email_footer),
        }
        return render_to_string("letters/_letter_reply_body.html", context)

    def set_dynamic_field_initial(self):
        self.fields["title"].initial = f"Re: {self.letter.title}"
        self.fields["html_body"].initial = self.get_html_body_with_footer()
        self.fields["html_quote"].initial = self.get_html_quote()
        print("form initialised")

    def add_form_buttons(self):
        if self.user_can_reply and self.user_can_save:
            self.helper.add_input(
                Submit("save", _("Save draft"), css_class="btn-default")
            )
            self.helper.add_input(
                Submit("send", _("Send reply"), css_class="btn-primary")
            )
        elif self.user_can_save:
            self.helper.add_input(
                Submit("save", _("Save draft"), css_class="btn-primary")
            )
        elif self.user_can_reply:
            self.helper.add_input(
                Submit("send", _("Send reply"), css_class="btn-primary")
            )

    def clean(self):
        self.cleaned_data["html_quote"] = self.get_html_quote()
        if not (self.user_can_reply or self.user_can_save):
            raise forms.ValidationError(
                _(
                    "Nothing to do. You do not have permission "
                    + "to save draft or send replies."
                )
            )
        if not self.user_can_reply and "send" in self.data:
            raise forms.ValidationError(
                _("You do not have permission to send replies.")
            )
        if not self.user_can_save and "save" in self.data:
            raise forms.ValidationError(_("You do not have permission to save draft."))
        return super().clean()

    def get_quote(self):
        quoted = text_email_wrapper(self.letter.body)
        return QUOTE_TPL.format(
            created=self.letter.created.strftime(settings.STRFTIME_FORMAT),
            email=self.letter.email_from,
            quoted=quoted,
        )

    def get_html_quote(self):
        html_body = (
            self.letter.html_body
            if is_formatted_html(self.letter.html_body)
            else text_to_html(self.letter.body)
        )
        quoted = "<blockquote>" + html_body + "</blockquote>"
        quote_info = QUOTE_TPL.format(
            created=self.letter.created.strftime(settings.STRFTIME_DATE_FORMAT),
            email=self.letter.email_from,
            quoted="",
        )
        html_quote = f"""
            <p>
                <br>
                {quote_info}<br>
                {quoted}
            </p>"""
        return mark_safe(html_quote)

    def save(self, *args, **kwargs):
        self.instance.author_user = self.user
        self.instance.body = html_to_text(self.cleaned_data["html_body"])
        self.instance.quote = html_to_text(self.cleaned_data["html_quote"])
        if not hasattr(self.instance, "record"):
            self.instance.record = Record.objects.create(case=self.letter.case)
        obj = super().save(*args, **kwargs)
        return obj

    class Meta:
        model = Letter
        fields = ["title", "html_body", "html_quote", "note"]


class AssignLetterForm(SingleButtonMixin, forms.Form):
    action_text = _("Assign")

    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop("letter")
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        # Field creation moved to init as multiple autocomplete widgets
        # on the same page need different ids to be identified properly
        # by autocomplete js functions
        self.fields["case"] = forms.ModelChoiceField(
            queryset=Case.objects.all(),
            label=_("Case number"),
            widget=autocomplete.ModelSelect2(
                url="cases:autocomplete-find",
                attrs={
                    "id": f"id_case_{self.letter.pk}",
                },
            ),
        )

    def save(self):
        self.letter.case = self.cleaned_data["case"]
        self.letter.record.save()
        self.letter.case.save()
        categorize_letter_in_background(self.letter.pk)
        messages.success(
            self.request,
            _(
                "Case was changed. Task to update letter"
                + " categorization and upadte normalized answers created"
            ),
        )


class ReassignLetterForm(SingleButtonMixin, forms.ModelForm):
    action_text = _("Reassign")

    case = forms.ModelChoiceField(
        queryset=Case.objects.all(),
        label=_("Case number"),
        widget=autocomplete.ModelSelect2(url="cases:autocomplete-find"),
    )

    def save(self, commit=True):
        self.instance.case = self.cleaned_data["case"]
        self.instance.record.save()
        return super().save(commit)
