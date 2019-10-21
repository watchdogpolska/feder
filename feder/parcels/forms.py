from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from dal import autocomplete
from django import forms

from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost
from feder.records.models import Record


class ParcelPostForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop("case")
        super(ParcelPostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.record = Record.objects.create(case=self.case)
        self.instance.created_by = self.user
        return super(ParcelPostForm, self).save(commit)


class IncomingParcelPostForm(ParcelPostForm):
    def __init__(self, *args, **kwargs):
        super(IncomingParcelPostForm, self).__init__(*args, **kwargs)
        self.initial["sender"] = self.case.institution

    class Meta:
        model = IncomingParcelPost
        fields = ["title", "content", "sender", "receive_date"]
        widgets = {"sender": autocomplete.ModelSelect2(url="institutions:autocomplete")}


class OutgoingParcelPostForm(ParcelPostForm):
    def __init__(self, *args, **kwargs):
        super(OutgoingParcelPostForm, self).__init__(*args, **kwargs)
        self.initial["recipient"] = self.case.institution

    class Meta:
        model = OutgoingParcelPost
        fields = ["title", "content", "recipient"]
        widgets = {
            "recipient": autocomplete.ModelSelect2(url="institutions:autocomplete")
        }
