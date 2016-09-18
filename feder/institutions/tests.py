# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from django.utils.encoding import force_text

from feder.main.mixins import PermissionStatusMixin
from feder.teryt.factories import JSTFactory
from feder.users.factories import UserFactory

from .factories import EmailFactory, InstitutionFactory, TagFactory
from .models import Institution
from .serializers import InstitutionSerializer
from .views import InstitutionAutocomplete, TagAutocomplete


class InstitutionTestCase(TestCase):
    def setUp(self):
        self.obj = InstitutionFactory(name="Example institution")

    def test_get_absolute_url(self):
        self.assertEqual(self.obj.get_absolute_url(),
                         '/institutions/example-institution')

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
        self.data = {
            "name": "xxx",
            "slug": "xxx",
            "tags": [
                "blabla", "X", "Z"
            ],
            "jst": JSTFactory().pk,
            "email_set": [{"email": "example-2@example.com"}, ]
        }

    def test_create_institution(self):
        serializer = InstitutionSerializer(data={
            'name': 'X',
            'jst': JSTFactory().pk,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertTrue(serializer.save())

    def test_create_institution_with_tags_and_email(self):
        TagFactory(name="X")  # for colission tag name
        serializer = InstitutionSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(qs=obj.tags.all(),
                                 values=["blabla", "X", "Z"],
                                 transform=force_text)
        self.assertQuerysetEqual(qs=obj.email_set.all(),
                                 values=["example-2@example.com"],
                                 transform=force_text)

    def test_update_institution_with_tags_and_email(self):
        institution = InstitutionFactory()

        self.data['pk'] = institution.pk
        del self.data['email_set']

        serializer = InstitutionSerializer(institution, data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(qs=obj.tags.all(),
                                 values=["blabla", "X", "Z"],
                                 transform=force_text)
        self.assertEqual(Institution.objects.count(), 1)  # updated

    def test_update_email_set_protected(self):
        institution = InstitutionFactory()
        email = EmailFactory(institution=institution)
        self.data['pk'] = institution.pk
        serializer = InstitutionSerializer(institution, data=self.data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(AssertionError):
            serializer.save()
        institution.refresh_from_db()
        self.assertQuerysetEqual(institution.email_set.all(), [repr(email)])


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.institution = InstitutionFactory()


class InstitutionListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse('institutions:list')
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'institutions/institution_filter.html')
        self.assertContains(response, self.institution.name)


class InstitutionDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

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


class InstitutionAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_by_name(self):
        InstitutionFactory(name='123')
        InstitutionFactory(name='456')
        request = self.factory.get('/customer/details', data={'q': '123'})
        response = InstitutionAutocomplete.as_view()(request)
        self.assertContains(response, '123')
        self.assertNotContains(response, '456')


class TagAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_by_name(self):
        TagFactory(name='123')
        TagFactory(name='456')
        request = self.factory.get('/customer/details', data={'q': '123'})
        response = TagAutocomplete.as_view()(request)
        self.assertContains(response, '123')
        self.assertNotContains(response, '456')

    def test_get_result_label_without_institution(self):
        TagFactory(name='123')
        request = self.factory.get('/customer/details', data={'q': '123'})
        response = TagAutocomplete.as_view()(request)
        self.assertContains(response, '123 (0)')

    def test_get_result_label_with_institution(self):
        institution = InstitutionFactory()
        institution.tags.add(TagFactory(name='123'))
        institution.save()

        request = self.factory.get('/customer/details', data={'q': '123'})
        response = TagAutocomplete.as_view()(request)
        self.assertContains(response, '123 (1)')
