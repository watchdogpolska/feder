from braces.views import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from guardian.mixins import PermissionRequiredMixin


class ExtraListMixin(object):
    paginate_by = 25
    extra_list_context = 'object_list'

    def paginator(self, object_list):
        paginator = Paginator(object_list, self.paginate_by)
        try:
            return paginator.page(self.kwargs.get('page', 1))
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            return paginator.page(paginator.num_pages)

    @staticmethod
    def get_object_list(obj):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super(ExtraListMixin, self).get_context_data(**kwargs)
        case_list = self.get_object_list(self.object)
        context[self.extra_list_context] = self.paginator(case_list)
        return context


class RaisePermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True
    redirect_unauthenticated_users = True


class AttrPermissionRequiredMixin(RaisePermissionRequiredMixin):
    permission_attribute = None

    @staticmethod
    def _resolve_path(obj, path=None):
        if path:
            for attr_name in path.split('__'):
                obj = getattr(obj, attr_name)
        return obj

    def get_permission_object(self):
        obj = super(AttrPermissionRequiredMixin, self).get_object()
        return self._resolve_path(obj, self.permission_attribute)

    def get_object(self):
        if not hasattr(self, 'object'):
            self.object = super(AttrPermissionRequiredMixin, self).get_object()
        return self.object


class AutocompletePerformanceMixin(object):
    select_only = None

    def choices_for_request(self, *args, **kwargs):
        qs = super(AutocompletePerformanceMixin, self).choices_for_request(*args, **kwargs)
        if self.select_only:
            qs = qs.only(*self.select_only)
        return qs
