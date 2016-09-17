from braces.views import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm
from django.core.exceptions import ImproperlyConfigured
from feder.users.factories import UserFactory


class ExtraListMixin(object):
    """Mixins for view to add additional paginated object list

    Attributes:
        extra_list_context (str): Name of extra list context
        paginate_by (int): Number of added objects per page
    """
    paginate_by = 25
    extra_list_context = 'object_list'

    def paginator(self, object_list):
        """A Method to paginate object_list accordingly.

        Args:
            object_list (QuerySet): A list of object to paginate

        Returns:
            Page: A page for current requests
        """
        paginator = Paginator(object_list, self.paginate_by)
        try:
            return paginator.page(self.kwargs.get('page', 1))
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
                '{0} is missing a permissions to assign. Define {0}.permission '
                'or override {0}.get_permission().'.format(self.__class__.__name__))

    def get_context_data(self, **kwargs):
        context = super(ExtraListMixin, self).get_context_data(**kwargs)
        object_list = self.get_object_list(self.object)
        context[self.extra_list_context] = self.paginator(object_list)
        return context


class RaisePermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Mixin to verify object permission with preserve correct status code in view
    """
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
    """A mixin to improve autocomplete to limit SELECTed fields

    Attributes:
        select_only (list): List of fields to select
    """
    select_only = None

    def choices_for_request(self, *args, **kwargs):
        qs = super(AutocompletePerformanceMixin, self).choices_for_request(*args, **kwargs)
        if self.select_only:
            qs = qs.only(*self.select_only)
        return qs


class PermissionStatusMixin(object):
    """Mixin to verify object permission status codes for different users

    Require user with username='john' and password='pass'

    Attributes:
        permission (TYPE): Description
        status_anonymous (int): Status code for anonymouser
        status_has_permission (int): Status code for user with permission
        status_no_permission (403): Status code for user without permission
        url (TYPE): url to test
    """
    url = None
    permission = None
    status_anonymous = 302
    status_no_permission = 403
    status_has_permission = 200

    def setUp(self):
        super(PermissionStatusMixin, self).setUp()
        self.user = getattr(self, 'user', UserFactory(username='john'))

    def get_url(self):
        """Get url to tests

        Returns:
            str: url to test

        Raises:
            ImproperlyConfigured: Missing a url to test
        """
        if self.url is None:
            raise ImproperlyConfigured(
                '{0} is missing a url to test. Define {0}.url '
                'or override {0}.get_url().'.format(self.__class__.__name__))
        return self.url

    def get_permission(self):
        """Returns the permission to assign for granted permission user

        Returns:
            list: A list of permission in format ```codename.permission_name```

        Raises:
            ImproperlyConfigured: Missing a permission to assign
        """
        if self.permission is None:
            raise ImproperlyConfigured(
                '{0} is missing a permissions to assign. Define {0}.permission '
                'or override {0}.get_permission().'.format(self.__class__.__name__))
        return self.permission

    def get_permission_object(self):
        """Returns object of permission-carrying object for grant permission
        """
        return getattr(self, 'permission_object', None)

    def grant_permission(self):
        """Grant permission to user in self.user

        Returns:
            TYPE: Description
        """
        for perm in self.get_permission():
            obj = self.get_permission_object()
            assign_perm(perm, self.user, obj)

    def login_permitted_user(self):
        """Login client to user with granted permissions

        """
        self.grant_permission()
        self.client.login(username='john', password='pass')

    def test_status_code_for_anonymous_user(self):
        """A test status code of response for anonymous user

        """
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_anonymous)

    def test_status_code_for_signed_user(self):
        """A test for status code of response for signed (logged-in) user

        Only login before test.
        """
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_no_permission)

    def test_status_code_for_privileged_user(self):
        """A test for status code of response for privileged user

        Grant permission to permission-carrying object and login before test
        """
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_has_permission)
