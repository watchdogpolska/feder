from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Fieldset, Layout
from dal import autocomplete
from django import forms

from .models import Institution


class InstitutionForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset("", "name", "jst", "regon", "email"),
            Fieldset("", "tags", css_class="form-group scrollable-widget"),
        )

    class Meta:
        model = Institution
        fields = ["name", "tags", "jst", "regon", "email"]
        widgets = {
            "jst": autocomplete.ModelSelect2(url="teryt:jst-autocomplete"),
            "tags": forms.CheckboxSelectMultiple,
        }
