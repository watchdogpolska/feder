from django.contrib.sites.shortcuts import get_current_site
from django.db.models.expressions import RawSQL
from rest_framework_csv.renderers import CSVStreamingRenderer


def get_numeric_param(request, key):
    """Get numeric param from request"""
    value = None
    try:
        value = int(request.POST.get(key))
    except (TypeError, ValueError):
        pass
    return value


def get_param(request, key):
    """Get numeric param from request"""
    value = None
    try:
        value = request.POST.get(key)
    except (TypeError, ValueError):
        pass
    return value


def get_full_url_for_context(path, context):
    scheme = (
        "{}://".format(context["request"].scheme)
        if "request" in context
        else "https://"
    )

    return "".join(
        [scheme, get_current_site(context.get("request", None)).domain, path]
    )


def get_clean_email(email: str) -> str:
    email = str(email)
    if "," in email:
        email = email.split(",")[0]
    email = email[-99:]
    if "<" in email:
        email = email.split("<")[1]
    if ">" in email:
        email = email.split(">")[0]
    return email


def get_email_domain(email: str) -> str:
    if "@" in email:
        return email.split("@")[1]
    return ""


class PaginatedCSVStreamingRenderer(CSVStreamingRenderer):
    def render(self, data, *args, **kwargs):
        """Copied form PaginatedCSVRenderer to support paginated results."""
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super().render(data, *args, **kwargs)


class FormattedDatetimeMixin:
    def with_formatted_datetime(self, field_name, timezone="UTC"):
        model = self.model
        table_name = model._meta.db_table
        expr = (
            f"CONVERT_TZ({table_name}.{field_name}, @@session.time_zone, '{timezone}')"
        )
        formatted_field_name = f"{field_name}_str"
        formatted_field_expr = RawSQL(
            f"DATE_FORMAT({expr}, '%%Y-%%m-%%d %%H:%%i:%%s')", []
        )
        return self.annotate(**{formatted_field_name: formatted_field_expr})


class RenderBooleanFieldMixin:
    def render_boolean_field(self, field):
        field_value = getattr(self, field)
        if field_value is None:
            return '<span class="fa fa-question"></span>'
        elif field_value:
            return '<span class="fa fa-check" style="color: green;"></span>'
        return '<span class="fa fa-times" style="color: red;"></span>'
