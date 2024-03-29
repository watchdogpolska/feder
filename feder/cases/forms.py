from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _

from feder.cases_tags.models import Tag

from .models import Case


class CaseForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop("monitoring", None)
        super().__init__(*args, **kwargs)
        self.instance.user = self.user
        if self.monitoring:
            self.instance.monitoring = self.monitoring

        monitoring = self.monitoring or getattr(self.instance, "monitoring")
        if monitoring:
            self.fields["tags"].queryset = Tag.objects.for_monitoring(monitoring).all()

    class Meta:
        model = Case
        fields = [
            "name",
            "institution",
            "is_quarantined",
            "confirmation_received",
            "response_received",
            "tags",
        ]
        widgets = {
            "institution": autocomplete.ModelSelect2(url="institutions:autocomplete"),
            "tags": forms.CheckboxSelectMultiple,
        }


class CaseTagFilterForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=autocomplete.Select2Multiple(),
        required=False,
        label=_("Tags"),
    )

    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop("monitoring", None)
        super().__init__(*args, **kwargs)
        if self.monitoring:
            self.fields["tags"].queryset = Tag.objects.for_monitoring(
                self.monitoring
            ).all()
