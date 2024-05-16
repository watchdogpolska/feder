import json
import logging

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.expressions import RawSQL
from django.forms.models import model_to_dict
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from rest_framework_csv.renderers import CSVStreamingRenderer

from feder.llm_evaluation.prompts import (
    NORMALIZED_RESPONSE_QUESTION_KEY,
    NORMALIZED_RESPONSE_ANSWER_KEY,
    NORMALIZED_RESPONSE_ANSWER_CATEGORY_KEY,
)

logger = logging.getLogger(__name__)


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


def render_normalized_response_html_table(normalized_response):
    html = "<table class='table table-bordered compact'>\n"
    html += (
        f"<tr><th>Nr</th><th>{NORMALIZED_RESPONSE_QUESTION_KEY}</th>"
        + f"<th>{NORMALIZED_RESPONSE_ANSWER_KEY}</th>"
        + f"<th>{NORMALIZED_RESPONSE_ANSWER_CATEGORY_KEY}</th></tr>\n"
    )
    try:
        for key, subdict in json.loads(normalized_response).items():
            html += (
                f"<tr><td>{key}</td>"
                + f"<td>{subdict.get(NORMALIZED_RESPONSE_QUESTION_KEY, '')}</td>"
                + f"<td>{subdict.get(NORMALIZED_RESPONSE_ANSWER_KEY, '')}</td>"
                + f"<td>{subdict.get(NORMALIZED_RESPONSE_ANSWER_CATEGORY_KEY, '')}"
                + "</td></tr>\n"
            )
        html += "</table>"
        return mark_safe(html)
    except json.JSONDecodeError:
        logger.warning(f"Normalized response is not valid JSON: {normalized_response}")
        return mark_safe(_("<p>Normalized response is not valid JSON.</p>"))


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


class FormValidLogEntryMixin:
    def form_valid(self, form):
        if self.object is None:
            action_flag = ADDITION
        else:
            action_flag = CHANGE
        response = super().form_valid(form)
        change_dict = {
            "changed": form.changed_data,
            "cleaned_data": form.cleaned_data,
        }
        LogEntry.objects.log_action(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(self.model).pk,
            object_id=self.object.pk,
            object_repr=force_str(self.object),
            action_flag=action_flag,
            change_message=f"{change_dict}",
        )
        return response


class LogEntryMixin:
    @staticmethod
    def create_log_entry(user, obj, action_flag, message=""):
        content_type = ContentType.objects.get_for_model(obj)
        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=content_type.pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=action_flag,
            change_message=message,
        )


class DeleteViewLogEntryMixin(LogEntryMixin):
    def post(self, request, *args, **kwargs):
        change_dict = {
            "deleted_data": model_to_dict(self.get_object()),
        }
        self.create_log_entry(
            user=self.request.user,
            obj=self.get_object(),
            action_flag=DELETION,
            message=f"{change_dict}",
        )
        return super().post(request, *args, **kwargs)
