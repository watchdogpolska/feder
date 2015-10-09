# -*- coding: utf-8 -*-
from autofixture import AutoFixture
from django.core.urlresolvers import reverse, reverse_lazy
from django.test import RequestFactory, TestCase
from guardian.shortcuts import assign_perm

from feder.institutions.models import Institution
from feder.teryt.models import JST

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class SetUpMixin(object):
    def _get_third_level_jst(self):
        jst = AutoFixture(JST,
                          field_values={'name': 'Kłodzko',
                                        'updated_on': '2015-02-12'},
                          generate_fk=True).create_one(commit=False)
        jst.rght = 0
        jst.save()
        JST.objects.rebuild()
        return jst

    @staticmethod
    def _assign_all_perm(user):
        assign_perm('institutions.change_institution', user)
        assign_perm('institutions.delete_institution', user)

    def _get_institution(self):
        jst = self._get_third_level_jst()
        institution = AutoFixture(Institution,
                                  field_values={'user': self.user,
                                                'jst': jst}).create_one()
        return institution

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='user', password='top_secret')
        self.sudo = User.objects.create_superuser(username="sudo",
                                                  email="wykop@wykop.pl",
                                                  password="top_secret")
        self.quest = User.objects.create_user(username='quest', password='top_secret')
        self.institution = self._get_institution()


class InstitutionViewTestCase(SetUpMixin, TestCase):
    def test_list_loads(self):
        response = self.client.get(reverse('institutions:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'institutions/institution_filter.html')
        self.assertContains(response, self.institution.name)

    def test_details_display(self):
        response = self.client.get(self.institution.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'institutions/institution_detail.html')
        self.assertContains(response, self.institution.name)

    def test_delete_post(self):
        url = reverse('institutions:delete', kwargs={'slug': self.institution.slug})
        self.assertTrue(Institution.objects.filter(pk=self.institution.pk).exists())
        self.client.login(username='sudo', password='top_secret')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('institutions:list'))
        self.assertFalse(Institution.objects.filter(pk=self.institution.pk).exists())


class PermCheckMixin(SetUpMixin):
    url = None
    contains = False
    template_name = 'institutions/institution_form.html'
    perm = None
    anonymous_user_status = 302
    non_permitted_status = 403
    permitted_status = 200

    def _get_url(self):
        return self.url

    def test_anonymous_user(self):
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.anonymous_user_status)

    def test_non_permitted_user(self):
        self.client.login(username='quest', password='top_secret')
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.non_permitted_status)

    def test_permitted_user(self):
        self.client.login(username='sudo', password='top_secret')
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, self.permitted_status)
        self.assertTemplateUsed(response, self.template_name)
        if self.contains:
            self.assertContains(response, self.institution.name)


class CreateViewPermTest(PermCheckMixin, TestCase):
    url = reverse('institutions:create')
    perm = 'institutions.add_institution'
    contains = False
    anonymous_user_status = 403


class UpdateViewPermTest(PermCheckMixin, TestCase):
    perm = 'institutions.change_institution'

    def _get_url(self):
        return reverse('institutions:update', kwargs={'slug': self.institution.slug})


class DeleteViewPermTest(PermCheckMixin, TestCase):
    perm = 'institutions.delete_institution'
    template_name = 'institutions/institution_confirm_delete.html'

    def _get_url(self):
        return reverse('institutions:delete', kwargs={'slug': self.institution.slug})
