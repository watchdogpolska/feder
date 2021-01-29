from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms
from .models import Tag


class TagForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop("monitoring", None)
        super().__init__(*args, **kwargs)
        if self.monitoring:
            self.instance.monitoring = self.monitoring

    class Meta:
        model = Tag
        fields = ["name"]
