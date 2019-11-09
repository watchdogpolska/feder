from atom.ext.crispy_forms.forms import SingleButtonMixin
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import Alert


class AlertForm(SingleButtonMixin, UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.monitoring = kwargs.pop("monitoring", None)
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.user.is_anonymous:
            self.instance.author = self.user
        if self.monitoring:
            self.instance.monitoring = self.monitoring

    class Meta:
        model = Alert
        fields = ["reason"]
