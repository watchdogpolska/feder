# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase
from feder.users.factories import UserFactory
from feder.main.mixins import PermissionStatusMixin

from .factories import InstitutionFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.institution = InstitutionFactory()


class InstitutionListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse('institutions:list')
    status_anonymous = 200
    status_no_permission = 200

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'institutions/institution_filter.html')
        self.assertContains(response, self.institution.name)


class InstitutionDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return self.institution.get_absolute_url()

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'institutions/institution_detail.html')
        self.assertContains(response, self.institution.name)


class InstitutionCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse('institutions:create')
    permission = ['institutions.add_institution', ]


class InstitutionUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['institutions.change_institution', ]

    def get_url(self):
        return reverse('institutions:update', kwargs={'slug': self.institution.slug})


class InstitutionDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['institutions.delete_institution', ]

    def get_url(self):
        return reverse('institutions:delete', kwargs={'slug': self.institution.slug})
