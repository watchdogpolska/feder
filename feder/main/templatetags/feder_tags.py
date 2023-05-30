from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from feder import get_version

register = template.Library()


@register.simple_tag
def feder_version():
    return get_version()


@register.simple_tag
def app_mode():
    """
    app_mode tag used to differentiate dev, demo and production environments
    use "DEV", "DEMO" and "PROD" values in env variable APP_MODE
    """
    if settings.APP_MODE == "PROD":
        return mark_safe("")
    return mark_safe(f'<h1 style="color: red;">{settings.APP_MODE}</h1>')


@register.simple_tag
def app_main_style():
    """
    app_main_style tag used to differentiate dev, demo and production environments
    use "DEV", "DEMO" and "PROD" values in env variable APP_MODE
    """
    if settings.APP_MODE == "PROD":
        return mark_safe('<div class="main">')
    elif settings.APP_MODE == "DEV":
        return mark_safe('<div class="main" style="background-color: #d3e20040;">)')
    return mark_safe('<div class="main" style="background-color: #60e20040;">)')


@register.filter
def boolean_icon(value):
    if value is None:
        return mark_safe('<span class="fa fa-question" style="color: gray;"></span>')
    elif value:
        return mark_safe('<span class="fa fa-check" style="color: green;"></span>')
    return mark_safe('<span class="fa fa-times" style="color: red;"></span>')
