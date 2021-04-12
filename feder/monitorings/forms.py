from atom.ext.crispy_forms.forms import SingleButtonMixin, HelperMixin
from atom.ext.guardian.forms import TranslatedUserObjectPermissionsForm
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Layout, Fieldset
from dal import autocomplete
from django import forms
from django.utils.translation import ugettext as _

from feder.users.models import User
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


class MassMessageForm(SingleButtonMixin, UserKwargModelFormMixin, forms.Form):
    subject = forms.CharField(max_length=80, required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)
    email_footer = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(_("Message"), "subject", "content", "email_footer"),
        )
