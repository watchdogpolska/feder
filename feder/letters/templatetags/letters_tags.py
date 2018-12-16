import re

from django import template

register = template.Library()

@register.filter
def remove_control_characters(text):
    """Removes all control characters
    Control characters are not supported in XML 1.0
    """
    return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text) if text else text
