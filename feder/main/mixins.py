from braces.views import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm
from django.core.exceptions import ImproperlyConfigured


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
#        print "View used %s" % (obj, )
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


class PermissionStatusMixin(object):
    url = None
    permission = []
    status_anonymous = 302
    status_no_permission = 403
    status_has_permission = 200

    def get_url(self):
        if self.url is None:
            raise ImproperlyConfigured(
                '{0} is missing a url to test. Define {0}.url '
                'or override {0}.get_url().'.format(self.__class__.__name__))
        return self.url

    def get_permission_object(self):
        if hasattr(self, 'permission_object'):
            return getattr(self, 'permission_object')

        if hasattr(self, 'object'):
            return getattr(self, 'object')
        raise ImproperlyConfigured(
            '{0} is missing a object to grant permission. Define '
            '{0}.permission_object or override '
            '{0}.get_permission_object().'.format(self.__class__.__name__))

    def grant_permission(self):
        for perm in self.permission:
            obj = self.get_permission_object()
#            print "Granted perm %s for %s" % (perm, obj)
            assign_perm(perm, self.user, obj)

    def test_status_code_for_anonymous_user(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_anonymous)

    def test_status_code_for_signed_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_no_permission)

    def test_status_code_for_privileged_user(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_has_permission)
