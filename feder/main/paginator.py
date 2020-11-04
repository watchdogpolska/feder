from base64 import b64decode, b64encode
from django.core.paginator import InvalidPage
from performant_pagination.pagination import PerformantPaginator, PerformantPage
import binascii

from rest_framework.pagination import PageNumberPagination


class ModernPerformantPaginator(PerformantPaginator):
    def validate_number(self, number):
        try:
            int(b64decode(number, validate=True))
            return number
        except (TypeError, binascii.Error):
            raise InvalidPage("Page number is invalid")

    def _object_to_token(self, obj):
        """
        Override to add support for Python 3
        See pull request of performant_pagination
        """
        field = self._field
        if field == "pk":
            value = obj._meta.pk.value_to_string(obj)
        else:
            pieces = field.split("__")
            if len(pieces) > 1:
                # traverse relationships, -1 will be our final field
                for piece in pieces[:-1]:
                    obj = getattr(obj, piece)
            # obj is now the object on which our final field lives
            value = obj._meta.get_field(pieces[-1]).value_to_string(obj)

        # return our value
        if isinstance(value, str):
            value = value.encode("utf-8")
        return b64encode(value).decode("utf-8")

    def page(self, token=None):
        """
        Override to add support for select_related (removed only)
        See pull request of performant_pagination
        """
        if token == 1:
            token = None

        qs = self.queryset
        if token:
            qs = qs.filter(**self._token_to_clause(token))

        qs = qs.order_by(self.ordering)

        object_list = list(qs[: self.per_page + 1])

        next_token = None
        if len(object_list) > self.per_page:
            object_list = object_list[:-1]
            next_token = self._object_to_token(object_list[-1])

        previous_token = None
        if token:
            clause = self._token_to_clause(token, rev=True)
            qs = self.queryset.filter(**clause).order_by(self._reverse_ordering)
            try:
                previous_token = self._object_to_token(qs[self.per_page - 1])
            except IndexError:
                previous_token = ""

        return PerformantPage(self, object_list, previous_token, token, next_token)


class DefaultPagination(PageNumberPagination):
    # increased maximum page size to allow export to CSV without pagination
    max_page_size = 10000
    page_size_query_param = "page_size"
