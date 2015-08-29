from __future__ import absolute_import
from django.core.urlresolvers import reverse
from django.utils import six
from django.test import TestCase
from feder.cases.factory import factory_case
from feder.institutions.factory import factory_institution
from ..models import Letter

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class ViewTestCase(TestCase):
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

    def _perm_check(self, url, template_name='letters/letter_form.html', contains=True):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='q', password='top_secret')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='X', password='top_secret')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        if contains:
            self.assertContains(response, six.text_type(self.l_user.title))

    def test_create_permission_check(self):
        self._perm_check(reverse('letters:create', kwargs={'case_pk': self.case.pk}),
                         contains=False)

    def test_update_permission_check(self):
        self._perm_check(reverse('letters:update',
                                 kwargs={'pk': self.l_user.pk}))

    def test_delete_permission_check(self):
        self._perm_check(reverse('letters:delete',
                                 kwargs={'pk': self.l_user.pk}),
                         template_name='letters/letter_confirm_delete.html')
