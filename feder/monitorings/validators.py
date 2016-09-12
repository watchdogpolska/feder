from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_template_syntax(value):
    if '{{EMAIL}}' not in value:
        raise ValidationError(_("Using field {{EMAIL}} is mandatory."))
