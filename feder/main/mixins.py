from functools import wraps
from types import MethodType

import django_filters
from django.db import models
from base64 import b64encode
from braces.views import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage, Paginator
from django.utils.http import urlencode
from django.views.generic.detail import BaseDetailView
from guardian.mixins import PermissionRequiredMixin
from django_sendfile import sendfile
from django.core.paginator import InvalidPage
from rest_framework_csv.renderers import CSVRenderer

from .paginator import ModernPerformantPaginator
from django.http import Http404
from django.utils.translation import ugettext as _


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


class RaisePermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
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


class AutocompletePerformanceMixin:
    """A mixin to improve autocomplete to limit SELECTed fields

    Attributes:
        select_only (list): List of fields to select
    """

    select_only = None

    def choices_for_request(self, *args, **kwargs):
        qs = super().choices_for_request(*args, **kwargs)
        if self.select_only:
            qs = qs.only(*self.select_only)
        return qs


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


class PerformantPagintorMixin:
    paginator_class = ModernPerformantPaginator
    first_page = b64encode(b"0").decode("utf-8")

    def paginate_queryset(self, queryset, page_size):
        """
        Overwrite pagination for support non-number paginator
        See https://github.com/django/django/pull/12429 for details
        """
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page = (
            self.kwargs.get(page_kwarg)
            or self.request.GET.get(page_kwarg)
            or self.first_page
        )
        try:
            page_number = paginator.validate_number(page)
        except (ValueError, InvalidPage):
            raise Http404(_("Page number is not valid."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(e)}
            )

    def get_context_data(self, **kwargs):
        """Insert the single object into the context dict."""
        context = {"pager": "performant"}
        context.update(kwargs)
        return super().get_context_data(**context)


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


class OrderedViewMixin:
    """
    Allows to set generic ordering options.
    Class members to be set in derived class:
        apply_order_to (str): name of class method returning queryset
            for which ordering should be applied
        order_param_name (str): name of the ordering GET parameter
        order_options (list(2 elem tuple)): list of available ordering options
            in form of (displayed name, queryset field name)
        default_ordering (list(str)): default arguments for order_by clause
            if order is not explicitly given
        order_limit (int|None): maximum number of ordering options to be applied
            simultaneously, None means no limit
    """

    apply_order_to = "get_object_list"
    order_param_name = "order_by"
    order_options = []
    order_default = []
    order_limit = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.order_current = None

        parent_method = getattr(self.__class__, self.apply_order_to)

        @wraps(parent_method)
        def wrapped(self_, *args_, **kwargs_):
            return parent_method(self_, *args_, **kwargs_).order_by(
                *self_.order_current
            )

        setattr(self, self.apply_order_to, MethodType(wrapped, self))

    def _set_order_current(self):
        order_by = self.request.GET.get(self.order_param_name, None)
        avail_fields = [o[1] for o in self.order_options]
        self.order_current = (
            [
                f
                for f in [i.strip() for i in order_by.split(",")]
                if f.strip("-") in avail_fields
            ]
            if order_by
            else self.order_default.copy()
        )

    def _get_ordering_url(self, order_field):
        get_params = {key: value for key, value in self.request.GET.items()}
        get_params.pop(self.order_param_name, None)

        order_list = self.order_current.copy()

        if order_field in order_list:
            order_list[order_list.index(order_field)] = f"-{order_field}"
        elif f"-{order_field}" in order_list:
            if len(order_list) > 1:
                order_list.remove(f"-{order_field}")
            else:
                # If this is the only selected option, just reverse ordering
                # instead of deleting the option from the order_list.
                order_list[order_list.index(f"-{order_field}")] = order_field
        else:
            order_list.append(order_field)

        if self.order_limit is not None:
            while len(order_list) > self.order_limit:
                del order_list[0]

        return "{}?{}".format(
            self.request.path,
            urlencode(
                dict(**get_params, **{self.order_param_name: ",".join(order_list)})
            ),
        )

    def get_context_data(self, **kwargs):
        self._set_order_current()
        context = super().get_context_data(**kwargs)

        order_dict = {}

        for option in self.order_options:
            order_dict[option[1]] = {
                "name": option[0],
                "field_name": option[1],
                "is_current": "",
                "url": self._get_ordering_url(option[1]),
            }
            if option[1] in self.order_current:
                order_dict[option[1]]["is_current"] = "+"
            if f"-{option[1]}" in self.order_current:
                order_dict[option[1]]["is_current"] = "-"
        context["order_dict"] = order_dict

        return context
