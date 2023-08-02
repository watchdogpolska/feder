import re

from django import template

register = template.Library()


@register.filter
def remove_control_characters(text):
    """Removes all control characters
    Control characters are not supported in XML 1.0
    """
    return re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", text) if text else text


@register.filter
def hide_email(value):
    """
    Replaces email addresses in a string with "{{ email }}"
    """
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.sub(email_regex, "{{ email }}", value)
