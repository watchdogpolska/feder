from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm

from feder.users.factories import UserFactory


class PermissionStatusMixin:
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
        super().setUp()

        self.user = getattr(self, "user", UserFactory(username="john"))

    def get_url(self):
        """Get url to tests

        Returns:
            str: url to test

        Raises:
            ImproperlyConfigured: Missing a url to test
        """
        if self.url is None:
            raise ImproperlyConfigured(
                "{0} is missing a url to test. Define {0}.url "
                "or override {0}.get_url().".format(self.__class__.__name__)
            )
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
                "{0} is missing a permissions to assign. Define {0}.permission "
                "or override {0}.get_permission().".format(self.__class__.__name__)
            )
        return self.permission

    def get_permission_object(self):
        """Returns object of permission-carrying object for grant permission
        """
        return getattr(self, "permission_object", None)

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
        self.client.login(username="john", password="pass")

    def test_status_code_for_anonymous_user(self):
        """A test status code of response for anonymous user

        """
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_anonymous)

    def test_status_code_for_signed_user(self):
        """A test for status code of response for signed (logged-in) user

        Only login before test.
        """
        self.client.login(username="john", password="pass")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_no_permission)

    def test_status_code_for_privileged_user(self):
        """A test for status code of response for privileged user

        Grant permission to permission-carrying object and login before test
        """
        self.grant_permission()
        self.client.login(username="john", password="pass")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.status_has_permission)


class HomeViewTestCase(TestCase):
    def test_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class SitemapTestCase(TestCase):
    def test_main(self):
        url = reverse("sitemaps", kwargs={"section": "main"})
        self.assertEqual(self.client.get(url).status_code, 200)
