import django_filters
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.paginator import EmptyPage, Paginator
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)
from django_sendfile import sendfile
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin
from rest_framework_csv.renderers import CSVRenderer


class ExtraListMixin:
    """Mixins for view to add additional paginated object list

    Attributes:
        extra_list_context (str): Name of extra list context
        paginate_by (int): Number of added objects per page
    """

    paginate_by = 25
    extra_list_context = "object_list"

    def paginator(self, object_list):
        """A Method to paginate object_list accordingly.

        Args:
            object_list (QuerySet): A list of object to paginate

        Returns:
            Page: A page for current requests
        """
        paginator = Paginator(object_list, self.paginate_by)
        try:
            return paginator.page(self.kwargs.get("page", 1))
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            return paginator.page(paginator.num_pages)

    def get_object_list(self, obj):
        """A method to return object list to additional list. This should be overriden.

        Args:
            obj: The object the view is displaying.

        Returns:
            QuerySet: A list of object to paginated
        Raises:
            ImproperlyConfigured: The method was not overrided.
        """
        raise ImproperlyConfigured(
            "{0} is missing a permissions to assign. Define {0}.permission "
            "or override {0}.get_permission().".format(self.__class__.__name__)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.get_object_list(self.object)
        context[self.extra_list_context] = self.paginator(object_list)
        return context


class AccessMixin:
    """Base for LoginRequiredMixin/PermissionRequiredMixin below (ported from the
    unmaintained django-braces, trimmed to what this project actually uses)."""

    raise_exception = False
    redirect_unauthenticated_users = False

    def handle_no_permission(self, request):
        if self.raise_exception:
            if (
                self.redirect_unauthenticated_users
                and not request.user.is_authenticated
            ):
                return self._redirect_to_login(request)
            raise PermissionDenied
        return self._redirect_to_login(request)

    @staticmethod
    def _redirect_to_login(request):
        return redirect_to_login(
            request.get_full_path(), settings.LOGIN_URL, REDIRECT_FIELD_NAME
        )


class LoginRequiredMixin(AccessMixin):
    """Requires the user to be authenticated (ported from django-braces)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(AccessMixin):
    """Requires request.user to have `permission_required` (ported from django-braces).

    Attributes:
        object_level_permissions (bool): check the permission against
            self.get_object() instead of globally.
    """

    permission_required = None
    object_level_permissions = False

    def check_permissions(self, request):
        if self.permission_required is None:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} requires the "permission_required" '
                "attribute to be set."
            )
        if self.object_level_permissions:
            obj = self.get_object() if hasattr(self, "get_object") else None
            return request.user.has_perm(self.permission_required, obj)
        return request.user.has_perm(self.permission_required)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_permissions(request):
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)


class RaisePermissionRequiredMixin(LoginRequiredMixin, GuardianPermissionRequiredMixin):
    """Mixin to verify object permission with preserve correct status code in view"""

    raise_exception = True
    redirect_unauthenticated_users = True


class AttrPermissionRequiredMixin(RaisePermissionRequiredMixin):
    """Mixin to verify object permission in SingleObjectView

    Attributes:
        permission_attribute (str): A path to traverse from object to permission object
    """

    permission_attribute = None

    @staticmethod
    def _resolve_path(obj, path=None):
        """Resolve django-like path eg. object2__object3 for object

        Args:
            obj: The object the view is displaying.
            path (str, optional): Description

        Returns:
            A oject at end of resolved path
        """
        if path:
            for attr_name in path.split("__"):
                obj = getattr(obj, attr_name)
        return obj

    def get_permission_object(self):
        obj = super().get_object()
        return self._resolve_path(obj, self.permission_attribute)

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = super().get_object()
        return self.object


class DisabledWhenFilterSetMixin(django_filters.filterset.BaseFilterSet):
    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            filter_ = self.filters[name]
            enabled_test = getattr(
                filter_, "check_enabled", lambda _: True
            )  # standard-filter compatible
            if not enabled_test(self.form.cleaned_data):
                continue
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '{}.{}' to return a QuerySet, but got a {} instead.".format(
                type(self).__name__,
                name,
                type(queryset).__name__,
            )
        return queryset


class DisabledWhenFilterMixin:
    def __init__(self, *args, **kwargs):
        self.disabled_when = kwargs.pop("disabled_when", [])
        super().__init__(*args, **kwargs)

    def check_enabled(self, form_data):
        return not any(form_data[field] for field in self.disabled_when)


class BaseXSendFileView(BaseDetailView):
    file_field = None
    send_as_attachment = None

    def get_file_field(self):
        return self.file_field

    def get_file_path(self, object):
        return getattr(object, self.get_file_field()).path

    def get_sendfile_kwargs(self, context):
        return dict(
            request=self.request,
            filename=self.get_file_path(context["object"]),
            attachment=self.send_as_attachment,
        )

    def render_to_response(self, context):
        return sendfile(**self.get_sendfile_kwargs(context))


class DisableOrderingListViewMixin:
    def get_queryset(self):
        return super().get_queryset().order_by("pk")


class CsvRendererViewMixin:
    """
    csv_serializer and default_serializer attributes can be set on derived class
    to be used accordingly with CSV and other renderers.
    """

    csv_file_name = _("data")

    def get_serializer_class(self):
        if isinstance(self.request.accepted_renderer, CSVRenderer):
            serializer = getattr(self, "csv_serializer", None)
        else:
            serializer = getattr(self, "default_serializer", None)
        return serializer or super().get_serializer_class()

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(self.request.accepted_renderer, CSVRenderer):
            response["Content-Disposition"] = "attachment; filename={}.csv".format(
                self.csv_file_name
            )
        return response


class SelectRelatedMixin:
    """Applies select_related for a list of relations (ported from django-braces)."""

    select_related = None

    def get_queryset(self):
        if self.select_related is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the select_related attribute."
            )
        return super().get_queryset().select_related(*self.select_related)


class PrefetchRelatedMixin:
    """Applies prefetch_related for a list of relations (ported from django-braces)."""

    prefetch_related = None

    def get_queryset(self):
        if self.prefetch_related is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the prefetch_related attribute."
            )
        return super().get_queryset().prefetch_related(*self.prefetch_related)


class UserFormKwargsMixin:
    """Includes request.user in the form kwargs (ported from django-braces)."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class FormValidMessageMixin:
    """Sends a success message via django.contrib.messages on valid form/delete
    (ported from django-braces)."""

    form_valid_message = None

    def get_form_valid_message(self):
        if self.form_valid_message is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}.form_valid_message is not set. Define "
                f"{self.__class__.__name__}.form_valid_message, or override "
                f"{self.__class__.__name__}.get_form_valid_message()."
            )
        return force_str(self.form_valid_message)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, self.get_form_valid_message(), fail_silently=True
        )
        return response

    def delete(self, *args, **kwargs):
        response = super().delete(*args, **kwargs)
        messages.success(
            self.request, self.get_form_valid_message(), fail_silently=True
        )
        return response


class SetHeadlineMixin:
    """Adds a `headline` context item from a view attribute (ported from
    django-braces)."""

    headline = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.headline is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the headline attribute."
            )
        context["headline"] = force_str(self.headline)
        return context


class MessageMixin:
    """Adds a `success_message` sent via django.contrib.messages (ported from
    django-atom)."""

    success_message = None

    def get_success_message(self):
        if self.success_message is None:
            raise NotImplementedError("Provide success_message or get_success_message")
        return self.success_message.format(**self.object.__dict__)


class DeleteMessageMixin:
    """Sends a success message on delete (ported from django-atom)."""

    hide_field = None

    def get_success_message(self):
        template = dict(object=self.object, verbose_name=self.model._meta.verbose_name)
        return _("{verbose_name} {object} deleted!").format(**template)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.hide_field:
            setattr(self.object, self.hide_field, False)
            self.object.save()
        else:
            self.object.delete()
        messages.add_message(request, messages.SUCCESS, self.get_success_message())
        return HttpResponseRedirect(success_url)


class ActionMixin:
    """Runs `action()` on POST and redirects to `success_url` (ported from
    django-atom)."""

    success_url = None

    def action(self):
        raise ImproperlyConfigured("No action to do. Provide a action body.")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.action()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return force_str(self.success_url).format(**self.object.__dict__)


class BaseActionView(ActionMixin, BaseDetailView):
    """Base view for an action on an object (ported from django-atom)."""


class ActionView(SingleObjectTemplateResponseMixin, BaseActionView):
    """ActionMixin with a `_action` template suffix (ported from django-atom)."""

    template_name_suffix = "_action"


class ActionMessageMixin(MessageMixin):
    """Sends a success message after ActionMixin.post() (ported from
    django-atom)."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.add_message(request, messages.SUCCESS, self.get_success_message())
        return response


class CreateMessageMixin:
    """Provides the "created" message text for FormValidMessageMixin (ported
    from django-atom)."""

    def get_form_valid_message(self):
        template = dict(object=self.object, verbose_name=self.model._meta.verbose_name)
        return _("{verbose_name} {object} created!").format(**template)


class UpdateMessageMixin:
    """Provides the "updated" message text for FormValidMessageMixin (ported
    from django-atom)."""

    def get_form_valid_message(self):
        template = dict(object=self.object, verbose_name=self.model._meta.verbose_name)
        return _("{verbose_name} {object} updated!").format(**template)


class UserKwargFilterSetMixin:
    """Includes request.user in the filterset kwargs (ported from
    django-atom)."""

    def get_filterset_kwargs(self, *args, **kwargs):
        kwargs = super().get_filterset_kwargs(*args, **kwargs)
        kwargs["user"] = self.request.user
        return kwargs
