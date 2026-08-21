from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext as _
from guardian.forms import UserObjectPermissionsForm


class HelperMixin:
    """Attaches a crispy_forms FormHelper instance (ported from django-atom)."""

    form_helper_cls = FormHelper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = getattr(self, "helper", self.form_helper_cls(self))


class SingleButtonMixin(HelperMixin):
    """Adds a single Save/Update submit button to the form layout (ported
    from django-atom)."""

    @property
    def action_text(self):
        return (
            _("Update") if hasattr(self, "instance") and self.instance.pk else _("Save")
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.add_input(
            Submit("action", self.action_text, css_class="btn-primary")
        )


class PermissionsTranslationMixin:
    """Translates guardian's permission choice labels (ported from
    django-atom)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(key, _(value)) for key, value in self.fields["permissions"].choices]
        self.fields["permissions"].choices = choices


class TranslatedUserObjectPermissionsForm(
    PermissionsTranslationMixin, UserObjectPermissionsForm
):
    """guardian's UserObjectPermissionsForm with translated permission labels
    (ported from django-atom)."""


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
