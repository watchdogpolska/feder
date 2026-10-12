from allauth.socialaccount.models import SocialApp
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.urls import reverse
from guardian.shortcuts import assign_perm

import feder
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
        self.user.user_permissions.add(
            Permission.objects.get(name="Can view Attachment")
        )

    def get_url(self):
        """Get url to tests

        Returns:
            str: url to test

        Raises:
            ImproperlyConfigured: Missing a url to test
        """
        if self.url is None:  # pragma: no cover
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
        if self.permission is None:  # pragma: no cover
            raise ImproperlyConfigured(
                "{0} is missing a permissions to assign. Define {0}.permission "
                "or override {0}.get_permission().".format(self.__class__.__name__)
            )
        return self.permission

    def get_permission_object(self):
        """Returns object of permission-carrying object for grant permission"""
        return getattr(self, "permission_object", None)

    def grant_permission(self, extra_permission=None):
        """Grant permission to user in self.user

        Returns:
            TYPE: Description
        """
        permission_list = self.get_permission()
        if extra_permission is not None:
            permission_list += (
                extra_permission
                if isinstance(extra_permission, (tuple, list))
                else [extra_permission]
            )
        for perm in self.get_permission():
            obj = self.get_permission_object()
            assign_perm(perm, self.user, obj)

    def login_permitted_user(self):
        """Login client to user with granted permissions"""
        self.grant_permission()
        self.client.login(username="john", password="pass")

    def test_status_code_for_anonymous_user(self):
        """A test status code of response for anonymous user"""
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

    def test_app_version(self):
        response = self.client.get(reverse("home"))
        app_version = feder.get_version()
        self.assertContains(response, app_version)


class FederBaseTests(TestCase):
    def test_has_version_attrs(self):
        self.assertTrue(hasattr(feder, "__version__"))

    def test_version(self):
        for x in feder.VERSION:
            self.assertTrue(isinstance(x, (int, str)))

    def test_get_version(self):
        self.assertTrue(isinstance(feder.get_version(), str))


class SitemapTestCase(TestCase):
    def test_main(self):
        url = reverse("sitemaps", kwargs={"section": "main"})
        self.assertEqual(self.client.get(url).status_code, 200)


class SignupTestCase(TestCase):
    def setUp(self):
        app = SocialApp.objects.create(
            provider="google", name="Google", client_id="id", secret="secret"
        )
        app.sites.add(Site.objects.get_current())

    @override_settings(ACCOUNT_ALLOW_SIGNUP=False)
    def test_signup_closed(self):
        response = self.client.get(reverse("account_signup"))
        self.assertTemplateUsed(response, "account/signup_closed.html")
        self.assertContains(response, reverse("account_login"))
        self.assertNotContains(response, "currently closed")

    @override_settings(ACCOUNT_ALLOW_SIGNUP=False)
    def test_login_hides_signup_links_when_closed(self):
        response = self.client.get(reverse("account_login"))
        self.assertFalse(response.context["signup_open"])
        self.assertNotContains(response, reverse("account_signup"))

    @override_settings(ACCOUNT_ALLOW_SIGNUP=True)
    def test_signup_open(self):
        response = self.client.get(reverse("account_signup"))
        self.assertTemplateUsed(response, "account/signup.html")

    @override_settings(ACCOUNT_ALLOW_SIGNUP=True)
    def test_login_shows_signup_links_when_open(self):
        response = self.client.get(reverse("account_login"))
        self.assertTrue(response.context["signup_open"])
        self.assertContains(response, reverse("account_signup"))


class NestedNextRedirectChainTestCase(TestCase):
    """Regression tests for the self-referential `?next=` chain that used
    to compound on every crawl of the login/signup pages (nesting observed
    up to 9 levels deep in production traffic)."""

    def assertNoNestedNext(self, response):
        content = response.content.decode()
        self.assertNotIn("next=/accounts/login", content)
        self.assertNotIn("next=/accounts/signup", content)
        self.assertNotIn("next=%2Faccounts%2Flogin", content)
        self.assertNotIn("next=%2Faccounts%2Fsignup", content)

    def test_login_collapses_nested_next_with_301(self):
        nested = "/accounts/login/?next=/listy/123"
        response = self.client.get(reverse("account_login"), {"next": nested})
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.headers["Location"],
            f"{reverse('account_login')}?next=%2Flisty%2F123",
        )

    @override_settings(ACCOUNT_ALLOW_SIGNUP=True)
    def test_signup_collapses_nested_next_with_301(self):
        nested = "/accounts/signup/?next=/listy/123"
        response = self.client.get(reverse("account_signup"), {"next": nested})
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.headers["Location"],
            f"{reverse('account_signup')}?next=%2Flisty%2F123",
        )

    def test_login_collapses_deeply_nested_next(self):
        nested = "/accounts/login/?next=/accounts/login/?next=/listy/123"
        response = self.client.get(reverse("account_login"), {"next": nested})
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.headers["Location"],
            f"{reverse('account_login')}?next=%2Flisty%2F123",
        )

    def test_login_with_flat_next_renders_without_redirect(self):
        response = self.client.get(reverse("account_login"), {"next": "/listy/123"})
        self.assertEqual(response.status_code, 200)
        self.assertNoNestedNext(response)

    def test_login_sidebar_link_does_not_nest_next(self):
        response = self.client.get(reverse("account_login"), {"next": "/listy/123"})
        self.assertContains(response, f"{reverse('account_login')}?next=%2Flisty%2F123")
        self.assertNoNestedNext(response)

    def test_login_sidebar_link_has_no_next_without_one(self):
        response = self.client.get(reverse("account_login"))
        self.assertNotContains(response, f"{reverse('account_login')}?next=")

    def test_home_sidebar_login_link_points_to_current_page(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, f"{reverse('account_login')}?next=%2F")

    def test_robots_txt_disallows_login_and_signup(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertContains(response, "Disallow: /accounts/login")
        self.assertContains(response, "Disallow: /accounts/signup")
