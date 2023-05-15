from textwrap import wrap

from atom.ext.crispy_forms.forms import HelperMixin, SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from tinymce.widgets import TinyMCE

from feder.cases.models import Case
from feder.letters.utils import get_body_with_footer
from feder.records.models import Record
from .models import Letter
from .utils import html_to_text, HtmlIframeWidget


QUOTE_TPL = "W nawiązaniu do pisma z dnia {created} z adresu {email}:\n{quoted}"


class LetterForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    case = forms.ModelChoiceField(
        queryset=Case.objects.all(),
        label=_("Case"),
        widget=autocomplete.ModelSelect2(url="cases:autocomplete-find"),
    )

    def __init__(self, *args, **kwargs):
        case = kwargs.pop("case", None)
        letter = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if letter and letter.is_mass_draft():
            del self.fields["case"]
        else:
            self.initial["case"] = case or letter.case
        self.helper.form_tag = False
        if letter.is_draft:
            self.fields["html_body"].widget = TinyMCE(
                attrs={
                    "cols": 80,
                    "rows": 20,
                },
            )
        else:
            self.fields["html_body"].widget = HtmlIframeWidget(
                attrs={
                    "cols": 80,
                    "rows": 20,
                },
            )
            self.fields["title"].widget.attrs["readonly"] = True
            self.fields["eml"].widget = forms.TextInput(attrs={"readonly": True})

    class Meta:
        model = Letter
        fields = ["title", "html_body", "case", "note", "eml"]

    def save(self, *args, **kwargs):
        self.instance.body = html_to_text(self.cleaned_data["html_body"])
        if not self.instance.is_mass_draft():
            self.instance.record.case = self.cleaned_data["case"]
            self.instance.record.save()
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

        self.set_dynamic_field_initial()
        self.add_form_buttons()

    def set_dynamic_field_initial(self):
        self.fields["title"].initial = f"Re: {self.letter.title}"
        self.fields["body"].initial = get_body_with_footer(
            "", self.letter.case.monitoring.email_footer
        )
        self.fields["quote"].initial = self.get_quote()

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
        quoted = "> " + "\n> ".join(wrap(self.letter.body, width=80))
        return QUOTE_TPL.format(
            created=self.letter.created.strftime(settings.STRFTIME_FORMAT),
            email=self.letter.email,
            quoted=quoted,
        )

    def save(self, *args, **kwargs):
        self.instance.author_user = self.user
        if not hasattr(self.instance, "record"):
            self.instance.record = Record.objects.create(case=self.letter.case)
        obj = super().save(*args, **kwargs)
        return obj

    class Meta:
        model = Letter
        fields = ["title", "body", "quote"]


class AssignLetterForm(SingleButtonMixin, forms.Form):
    action_text = _("Assign")

    def __init__(self, *args, **kwargs):
        self.letter = kwargs.pop("letter")
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
