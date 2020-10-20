from braces.forms import UserKwargModelFormMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from dal import autocomplete
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Institution


class InstitutionForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form "helper" is needed to have control over rendering by "crispy" tag.
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("", "name", "jst", "regon", "email"),
            Fieldset("", "tags", css_class="form-group scrollable-widget"),
            ButtonHolder(Submit("submit", _("Update"), css_class="btn btn-primary")),
        )

    class Meta:
        model = Institution
        fields = ["name", "tags", "jst", "regon", "email"]
        widgets = {
            "jst": autocomplete.ModelSelect2(url="teryt:community-autocomplete"),
            "tags": forms.CheckboxSelectMultiple,
        }
