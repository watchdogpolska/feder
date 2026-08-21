from crispy_forms.helper import FormHelper
from django.forms.models import BaseInlineFormSet


class UserKwargModelFormMixin:
    """Pops `user` out of the form kwargs and attaches it to the instance
    (ported from django-braces). Must precede forms.ModelForm/forms.Form."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class BaseTableFormSetB3(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        h = FormHelper()
        h.template_pack = "bootstrap3"
        h.template = "bootstrap3/table_inline_formset.html"
        h.form_tag = False  # outer <form> is in the page template
        self.helper = h
