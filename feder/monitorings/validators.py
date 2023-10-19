from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_template_syntax(value):
    if "{{EMAIL}}" not in value:
        raise ValidationError(_("Using field {{EMAIL}} is mandatory."))


def validate_nested_lists(value):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(value, "html.parser")
    for tag in soup.find_all(["ul", "ol"]):
        if tag.parent.name in ["ul", "ol", "li"]:
            raise ValidationError(
                _("Do not use HTML nested lists - not readable in text mail clients.")
            )
