from django import template
from feder import get_version

register = template.Library()


@register.simple_tag
def feder_version():
    return get_version()
