# -*- coding: utf-8 -*-
from autofixture import AutoFixture
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from guardian.shortcuts import assign_perm

from feder.institutions.models import Institution
from feder.teryt.models import JednostkaAdministracyjna

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class InstitutionViewTestCase(TestCase):

    def _get_third_level_jst(self):
        jst = AutoFixture(JednostkaAdministracyjna,
                          field_values={'name': 'Kłodzko',
                                        'updated_on': '2015-02-12'},
                          generate_fk=True).create_one(commit=False)
        jst.rght = 0
        jst.save()
        JednostkaAdministracyjna.objects.rebuild()
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
        self.user = User.objects.create_user(username='user-1', password='test')
        self.institution = self._get_institution()

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

    def _perm_check(self, url, perm, template_name='institutions/institution_form.html',
                    contains=True):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        assign_perm('institutions.' + perm, self.user)
        self.client.login(username='user-1', password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        if contains:
            self.assertContains(response, self.institution.name)

    def test_create_permission_check(self):
        self._perm_check(reverse('institutions:create'), 'add_institution', contains=False)

    def test_update_permission_check(self):
        self._perm_check(reverse('institutions:update',
                                 kwargs={'slug': self.institution.slug}),
                         'change_institution')

    def test_delete_permission_check(self):
        url = reverse('institutions:delete', kwargs={'slug': self.institution.slug})
        self._perm_check(url,
                         'delete_institution',
                         template_name='institutions/institution_confirm_delete.html')

    def test_delete_post(self):
        url = reverse('institutions:delete', kwargs={'slug': self.institution.slug})
        self.assertTrue(Institution.objects.filter(pk=self.institution.pk).exists())
        assign_perm('institutions.delete_institution', self.user)
        self.client.login(username='user-1', password='test')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('institutions:list'))
        self.assertFalse(Institution.objects.filter(pk=self.institution.pk).exists())
