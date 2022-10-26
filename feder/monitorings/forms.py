from textwrap import wrap
from atom.ext.crispy_forms.forms import SingleButtonMixin, HelperMixin
from atom.ext.guardian.forms import TranslatedUserObjectPermissionsForm
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Layout, Fieldset, Submit
from dal import autocomplete
from django import forms
from django.utils.translation import gettext as _
from django.conf import settings

from feder.users.models import User
from feder.letters.models import Letter, MassMessageDraft
from feder.letters.utils import get_body_with_footer, BODY_REPLY_TPL
from feder.letters.forms import QUOTE_TPL
from feder.cases_tags.models import Tag
from feder.letters.models import Record
from .models import Monitoring


class MonitoringForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # disable fields for create
            del self.fields["notify_alert"]
        self.instance.user = self.user
        self.helper.layout = Layout(
            Fieldset(_("Monitoring"), "name", "description", "notify_alert"),
            Fieldset(_("Template"), "subject", "template", "email_footer", "domain"),
        )
        self.fields["template"].initial = BODY_REPLY_TPL

    class Meta:
        model = Monitoring
        fields = [
            "name",
            "description",
            "notify_alert",
            "subject",
            "template",
            "email_footer",
            "domain",
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
    return "{} ({})".format(obj.name, obj.cases_count)


class MassMessageForm(HelperMixin, UserKwargModelFormMixin, forms.ModelForm):
    recipients_tags = forms.ModelMultipleChoiceField(
        label=_("Recipient's tags"),
        help_text=None,
        widget=forms.CheckboxSelectMultiple,
        queryset=Tag.objects.none(),
    )

    class Meta:
        model = Letter
        fields = ["recipients_tags", "title", "body", "quote", "note"]

    def __init__(self, monitoring, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.monitoring = monitoring
        self.application_letter = self.get_application_letter()
        self.user_can_reply = self.user.has_perm("reply", monitoring)
        self.user_can_save = self.user.has_perm("add_draft", monitoring)

        self.fields["recipients_tags"].queryset = Tag.objects.for_monitoring(
            obj=monitoring
        )
        self.fields[
            "recipients_tags"
        ].label_from_instance = recipients_tags_label_from_instance
        self.fields["body"].help_text = _("Use {{EMAIL}} to insert reply address.")

        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(_("Message"), "recipients_tags", "title", "body", "quote", "note"),
        )
        self.set_dynamic_field_initial()
        self.add_form_buttons()

    def get_application_letter(self):
        case = self.monitoring.case_set.order_by("created").first()
        return (
            Letter.objects.filter(record__case=case, author_user_id__isnull=False)
            .order_by("created")
            .first()
        )

    def set_dynamic_field_initial(self):
        if self.application_letter:
            self.fields["title"].initial = "Re: {title}".format(
                title=self.application_letter.title
            )
            self.fields["body"].initial = get_body_with_footer(
                "", self.monitoring.email_footer
            )
            self.fields["quote"].initial = self.get_quote()

    def add_form_buttons(self):
        if self.user_can_save:
            self.helper.add_input(
                Submit("save", _("Save draft"), css_class="btn-primary")
            )
        if self.user_can_reply:
            self.helper.add_input(
                Submit("send", _("Send message"), css_class="btn-primary")
            )

    def get_quote(self):
        quoted = "> " + "\n> ".join(wrap(self.application_letter.body, width=80))
        return QUOTE_TPL.format(
            created=self.application_letter.created.strftime(settings.STRFTIME_FORMAT),
            email=self.application_letter.email,
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
