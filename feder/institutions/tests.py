# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_text

from feder.main.mixins import PermissionStatusMixin
from feder.users.factories import UserFactory

from .factories import EmailFactory, InstitutionFactory, TagFactory
from .models import Institution
from .serializers import InstitutionSerializer
from feder.teryt.factories import JSTFactory


class InstitutionTestCase(TestCase):
    def setUp(self):
        self.obj = InstitutionFactory(name="Example institution")

    def test_get_absolute_url(self):
        self.assertEqual(self.obj.get_absolute_url(),
                         '/institutions/institution-example-institution')

    def test_get_str(self):
        self.assertEqual(force_text(self.obj),
                         "Example institution")

    def test_accurate_email_empty(self):
        self.assertEqual(self.obj.accurate_email, None)

    def test_accurate_email_select(self):
        EmailFactory(institution=self.obj, priority=1)
        high = EmailFactory(institution=self.obj, priority=2)
        self.assertEqual(self.obj.accurate_email, high)

        del self.obj.__dict__['accurate_email']
        higher = EmailFactory(institution=self.obj, priority=3)
        self.assertEqual(self.obj.accurate_email, higher)

        del self.obj.__dict__['accurate_email']
        EmailFactory(institution=self.obj, priority=0)
        self.assertEqual(self.obj.accurate_email, higher)

    def test_accurate_email_prefetch_empty(self):
        qs = Institution.objects.with_accurate_email()
        self.assertEqual(qs.get(pk=self.obj.pk).accurate_email, None)

    def test_accurate_email_prefetch_select(self):
        qs = Institution.objects.with_accurate_email()

        EmailFactory(institution=self.obj, priority=1)
        high = EmailFactory(institution=self.obj, priority=2)
        self.assertEqual(qs.get(pk=self.obj.pk).accurate_email, high)

        higher = EmailFactory(institution=self.obj, priority=3)
        self.assertEqual(qs.get(pk=self.obj.pk).accurate_email, higher)

        EmailFactory(institution=self.obj, priority=0)
        self.assertEqual(qs.get(pk=self.obj.pk).accurate_email, higher)


class InstitutionSerializerTestCase(TestCase):
    def setUp(self):
        self.jst = JSTFactory()

    def test_create_institution(self):
        serializer = InstitutionSerializer(data={
            'name': 'X',
            'jst': self.jst.pk,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertTrue(serializer.save())

    def test_create_institution_with_tags_and_email(self):
        TagFactory(name="X")
        serializer = InstitutionSerializer(data={
            "name": "xxx",
            "slug": "xxx",
            "tags": [
                "blabla", "X", "Z"
            ],
            "jst": self.jst.pk,
            "email_set": [{
                "email": "example-2@example.com",
            }
            ]
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(qs=obj.tags.all(),
                                 values=["blabla", "X", "Z"],
                                 transform=force_text)
        self.assertQuerysetEqual(qs=obj.email_set.all(),
                                 values=["example-2@example.com"],
                                 transform=force_text)


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
