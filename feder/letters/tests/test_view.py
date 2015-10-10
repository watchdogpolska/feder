from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import six

from feder.cases.factories import factory_case
from feder.institutions.factories import factory_institution

from ..models import Letter

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class SetUpMixin(object):
      def setUp(self):
        self.user = User.objects.create_user(username='jacob',
                                             email='jacob@example.com',
                                             password='top_secret')
        self.sudo = User.objects.create_superuser(username="X",
                                                  email='xx@example.com',
                                                  password="top_secret")
        self.quest = User.objects.create_user(username="q",
                                              password="top_secret")
        self.case = factory_case(self.user)
        self.l_user = Letter.objects.create(author_user=self.user,
                                            case=self.case,
                                            title="Wniosek",
                                            body="Prosze przeslac informacje",
                                            email="X@wykop.pl")

        self.institution = factory_institution(self.user)
        self.l_institution = Letter.objects.create(author_institution=self.institution,
                                                   case=self.case,
                                                   title="Odpowiedz",
                                                   body="W zalaczeniu.",
                                                   email="karyna@gmina.pl")


class ViewTestCase(SetUpMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse('letters:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'letters/letter_filter.html')
        self.assertContains(response, 'Odpowiedz')
        self.assertContains(response, 'Wniosek')

    def test_details_display(self):
        response = self.client.get(self.l_user.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'letters/letter_detail.html')
        self.assertContains(response, self.l_user.title)


class PermCheckMixin(SetUpMixin):
    url = None
    contains = True
    template_name = 'letters/letter_form.html'
    perm = None
    anonymous_user_status = 302
    non_permitted_status = 403
    permitted_status = 200

    def login(self):
        self.client.login(username='q', password='top_secret')

    def login_permitted(self):
        self.client.login(username='X', password='top_secret')

    def test_anonymous_user(self):
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.anonymous_user_status)

    def test_non_permitted_user(self):
        self.login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.non_permitted_status)

    def test_permitted_user(self):
        self.login_permitted()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.permitted_status)
        self.assertTemplateUsed(response, self.template_name)
        if self.contains:
            self.assertContains(response, six.text_type(self.l_user.title))


class CreatePermissionTestCase(PermCheckMixin, TestCase):
    contains = False

    def _get_url(self):
        return reverse('letters:create', kwargs={'case_pk': self.case.pk})


class UpdatePermissionTestCase(PermCheckMixin, TestCase):
    def _get_url(self):
        return reverse('letters:update', kwargs={'pk': self.l_user.pk})


class DeletePermissionTestCase(PermCheckMixin, TestCase):
    template_name = 'letters/letter_confirm_delete.html'

    def _get_url(self):
        return reverse('letters:delete', kwargs={'pk': self.l_user.pk})


class ReplyPermissionTestCase(PermCheckMixin, TestCase):
    template_name = 'letters/letter_reply.html'

    def _get_url(self):
        return reverse('letters:reply', kwargs={'pk': self.l_user.pk})
