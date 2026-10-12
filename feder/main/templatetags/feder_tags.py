from urllib.parse import quote

from bleach.sanitizer import Cleaner
from django import template
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse
from django.utils.safestring import mark_safe

from feder import get_version
from feder.main.utils import collapse_next_url

BODY_REPLY_TPL = "\n\nProsimy o odpowiedź na adres {{EMAIL}}"
BODY_FOOTER_SEPERATOR = "\n\n--\n"


cleaner = Cleaner(
    tags=settings.BLEACH_ALLOWED_TAGS,
    attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
    strip=True,
)

register = template.Library()


@register.simple_tag
def feder_version():
    return get_version()


@register.simple_tag
def sentry_dsn():
    """
    Exposes the same SENTRY_DSN used by the backend (config/settings/production.py)
    to the frontend, so @sentry/browser only activates where the server-side
    Sentry integration is already configured.
    """
    return getattr(settings, "SENTRY_DSN", "")


@register.simple_tag
def app_mode_value():
    return settings.APP_MODE


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
        return mark_safe('<span class="fas fa-question" style="color: gray;"></span>')
    elif value:
        return mark_safe('<span class="fas fa-check" style="color: green;"></span>')
    return mark_safe('<span class="fa-solid fa-xmark" style="color: red;"></span>')


@register.filter
def sanitize_html(value):
    return mark_safe(cleaner.clean(value))


@register.simple_tag
def show_donate_popup():
    """
    show_donate_popup tag used to display donate popup between Jan 1 and May 2nd
    inclusive, every year
    """
    from datetime import datetime

    now = datetime.now()
    if (1 <= now.month <= 4) or (now.month == 5 and now.day in [1, 2]):
        return True
    return False


@register.filter
def underscores_to_spaces(value):
    return value.replace("_", " ")


@register.filter
def spaces_to_underscores(value):
    return value.replace(" ", "_")


@register.simple_tag(takes_context=True)
def login_url_with_next(context):
    """
    Safe login URL for the sitewide "Log In" link. On the login/signup
    pages themselves, reuse (and collapse) their own `next` instead of
    wrapping a brand-new layer around the current, already-`next`-carrying
    URL -- that re-wrapping is what produced self-referential, ever-deepening
    `?next=` chains for crawlers.
    """
    request = context["request"]
    url_name = request.resolver_match.url_name if request.resolver_match else None
    if url_name in ("account_login", "account_signup"):
        target = collapse_next_url(request.GET.get(REDIRECT_FIELD_NAME), request)
    else:
        target = request.get_full_path()
    login_url = reverse("account_login")
    if not target:
        return login_url
    return f"{login_url}?{REDIRECT_FIELD_NAME}={quote(target, safe='')}"
