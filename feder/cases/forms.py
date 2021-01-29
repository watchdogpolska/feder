from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from dal import autocomplete
from django import forms
from .models import Case
from feder.cases_tags.models import Tag


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
        fields = ["name", "institution", "tags"]
        widgets = {
            "institution": autocomplete.ModelSelect2(url="institutions:autocomplete"),
            "tags": forms.CheckboxSelectMultiple,
        }
