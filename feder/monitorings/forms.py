from atom.ext.crispy_forms.forms import HelperMixin, SingleButtonMixin
from atom.ext.guardian.forms import TranslatedUserObjectPermissionsForm
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Column, Fieldset, Layout, Row, Submit
from dal import autocomplete
from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from tinymce.widgets import TinyMCE

from feder.cases_tags.models import Tag
from feder.letters.forms import QUOTE_TPL
from feder.letters.models import Letter, MassMessageDraft, Record
from feder.letters.utils import (
    BODY_REPLY_TPL,
    html_to_text,
    is_formatted_html,
    text_email_wrapper,
    text_to_html,
)
from feder.users.models import User

from .models import Monitoring


class MonitoringForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # disable fields for create
            del self.fields["notify_alert"]
        if self.instance.template and not is_formatted_html(self.instance.template):
            self.initial["template"] = mark_safe(text_to_html(self.instance.template))
        self.instance.user = self.user
        if not self.instance.use_llm:
            self.fields["use_llm"].help_text = _(
                "Before enabling, make sure that the content of the application will no"
                + " longer be changed. You can always go back to edit and enable later."
            )
        if not self.user.is_superuser:
            del self.fields["use_llm"]
        self.fields["template"].initial = BODY_REPLY_TPL
        self.fields["template"].widget = TinyMCE(attrs={"cols": 80, "rows": 20})
        if self.instance.use_llm:
            self.fields["template"].help_text = _(
                "Use {{EMAIL}} for insert reply address. \n"
                + "NOTE: LLM use is enabled. This means that any interference with the"
                + " application template may significantly disturb the credibility of"
                + " the results. If applications have already been sent to some"
                + " institutions during this monitoring period and you still need to"
                + " change the application template, consider setting up a new"
                + " monitoring query."
            )
        self.fields["email_footer"].widget = TinyMCE(attrs={"cols": 80, "rows": 5})
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        _("Monitoring"),
                        "name",
                        "description",
                        "notify_alert",
                        "is_public",
                        "hide_new_cases",
                        "use_llm",
                    ),
                    css_class="form-group col-md-5 mb-0",
                ),
                Column(
                    Fieldset(
                        _("Template"), "subject", "template", "email_footer", "domain"
                    ),
                    css_class="form-group col-md-7 mb-0",
                ),
            ),
        )

    class Meta:
        model = Monitoring
        fields = [
            "name",
            "description",
            "notify_alert",
            "hide_new_cases",
            "is_public",
            "use_llm",
            "subject",
            "template",
            "email_footer",
            "domain",
        ]


class MonitoringResultsForm(
    SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = self.user
        self.fields["results"].widget = TinyMCE(attrs={"cols": 80, "rows": 25})
        self.fields["subject"].widget.attrs["readonly"] = True
        self.fields["name"].widget.attrs["readonly"] = True
        self.fields["description"].widget.attrs["readonly"] = True
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        _("Monitoring info"),
                        "name",
                        "description",
                    ),
                    css_class="form-group col-md-5 mb-0",
                ),
                Column(
                    Fieldset(_("Monitoring results"), "subject", "results"),
                    css_class="form-group col-md-7 mb-0",
                ),
            ),
        )

    class Meta:
        model = Monitoring
        fields = [
            "name",
            "description",
            "subject",
            "results",
        ]


class SelectUserForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url="users:autocomplete"),
        label=_("User"),
    )


class CheckboxTranslatedUserObjectPermissionsForm(
    HelperMixin, TranslatedUserObjectPermissionsForm
):
    def get_obj_perms_field_widget(self):
        return forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset("", "permissions", css_class="form-group checkbox-utils"),
        )


class SaveTranslatedUserObjectPermissionsForm(
    SingleButtonMixin, CheckboxTranslatedUserObjectPermissionsForm
):
    pass


def recipients_tags_label_from_instance(obj):
    return f"{obj.name} ({obj.cases_count})"


class MassMessageForm(HelperMixin, UserKwargModelFormMixin, forms.ModelForm):
    recipients_tags = forms.ModelMultipleChoiceField(
        label=_("Recipient's tags"),
        help_text=None,
        widget=forms.CheckboxSelectMultiple,
        queryset=Tag.objects.none(),
    )

    class Meta:
        model = Letter
        fields = ["recipients_tags", "title", "html_body", "html_quote", "note"]

    def __init__(self, monitoring, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.monitoring = monitoring
        self.application_letter = self.get_application_letter()
        self.user_can_reply = self.user.has_perm("reply", monitoring)
        self.user_can_save = self.user.has_perm("add_draft", monitoring)

        self.fields["recipients_tags"].queryset = Tag.objects.for_monitoring(
            obj=monitoring
        )
        self.fields["recipients_tags"].label_from_instance = (
            recipients_tags_label_from_instance
        )
        self.fields["html_body"].help_text = _("Use {{EMAIL}} to insert reply address.")

        self.helper.form_tag = False
        self.fields["html_body"].widget = TinyMCE(attrs={"cols": 80, "rows": 20})
        self.fields["html_quote"].widget = TinyMCE(attrs={"cols": 80, "rows": 20})
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(_("Message"), "recipients_tags", "title", "html_body"),
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

    def get_application_letter(self):
        case = self.monitoring.case_set.order_by("created").first()
        application_letter = (
            Letter.objects.filter(record__case=case, author_user__isnull=False)
            .order_by("created")
            .first()
        )
        return application_letter

    def set_dynamic_field_initial(self):
        self.fields["html_body"].initial = self.get_html_body_with_footer()
        if self.application_letter:
            self.fields["title"].initial = "Re: {title}".format(
                title=self.application_letter.title
            )
            self.fields["html_quote"].initial = self.get_html_quote()

    def add_form_buttons(self):
        if self.user_can_save:
            self.helper.add_input(
                Submit("save", _("Save draft"), css_class="btn-primary")
            )
        if self.user_can_reply:
            self.helper.add_input(
                Submit("send", _("Send message"), css_class="btn-primary")
            )

    def get_html_body_with_footer(self):
        reply_info = BODY_REPLY_TPL.replace("\n", "<br>\n")
        context = {
            "html_body": mark_safe(f"<p>{reply_info}</p>"),
            "html_footer": mark_safe(self.monitoring.email_footer),
        }
        return render_to_string("letters/_letter_reply_body.html", context)

    def get_html_quote(self):
        html_body = (
            self.application_letter.html_body
            if is_formatted_html(self.application_letter.html_body)
            else text_to_html(self.application_letter.body)
        )
        quoted = "<blockquote>" + html_body + "</blockquote>"
        quote_info = QUOTE_TPL.format(
            created=self.application_letter.created.strftime(
                settings.STRFTIME_DATE_FORMAT
            ),
            email="{{EMAIL}}",
            quoted="",
        )
        html_quote = f"""
            <p>
                <br>
                {quote_info}<br>
                {quoted}
            </p>"""
        return mark_safe(html_quote)

    def get_text_quote(self):
        quoted = text_email_wrapper(self.application_letter.body)
        return QUOTE_TPL.format(
            created=self.application_letter.created.strftime(
                settings.STRFTIME_DATE_FORMAT
            ),
            email="{{EMAIL}}",
            quoted=quoted,
        )

    def clean(self):
        if not self.user_can_reply and "send" in self.data:
            raise forms.ValidationError(
                _("You do not have permission to send messages.")
            )
        if not self.user_can_save and "save" in self.data:
            raise forms.ValidationError(_("You do not have permission to save draft."))
        return super().clean()

    def save(self, commit=True):
        self.instance.message_type = Letter.MESSAGE_TYPES.mass_draft
        self.instance.is_draft = True
        self.instance.author_user = self.user
        self.instance.body = html_to_text(self.instance.html_body)
        self.instance.quote = html_to_text(self.instance.html_quote)
        self.instance.record = Record.objects.create()
        letter = super().save(commit=commit)
        return letter

    def _save_m2m(self):
        super()._save_m2m()
        draft = MassMessageDraft(
            letter=self.instance,
            monitoring=self.monitoring,
        )
        draft.save()
        draft.recipients_tags.set(self.cleaned_data["recipients_tags"])
