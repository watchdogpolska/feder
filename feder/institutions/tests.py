# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from django.utils.encoding import force_text

from feder.main.mixins import PermissionStatusMixin
from feder.teryt.factories import JSTFactory
from feder.users.factories import UserFactory
from .factories import InstitutionFactory, TagFactory
from .models import Institution
from .serializers import InstitutionSerializer
from .views import InstitutionAutocomplete, TagAutocomplete


class InstitutionTestCase(TestCase):
    def setUp(self):
        self.obj = InstitutionFactory(name="Example institution")

    def test_get_absolute_url(self):
        self.assertEqual(self.obj.get_absolute_url(),
                         '/instytucje/example-institution')

    def test_get_str(self):
        self.assertEqual(force_text(self.obj),
                         "Example institution")


class InstitutionSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {
            "name": "xxx",
            "slug": "xxx",
            "tags": [
                "blabla", "X", "Z"
            ],
            "jst": JSTFactory().pk,
            "email": "example-2@example.com",
        }

    def test_create_institution(self):
        serializer = InstitutionSerializer(data={
            'name': 'X',
            "email": "example-2@example.com",
            'jst': JSTFactory().pk,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertTrue(serializer.save())

    def test_create_institution_with_tags(self):
        TagFactory(name="X")  # for colission tag name
        serializer = InstitutionSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(qs=obj.tags.all(),
                                 values=["blabla", "X", "Z"],
                                 transform=force_text)

    def test_update_institution_with_tags(self):
        institution = InstitutionFactory()

        self.data['pk'] = institution.pk

        serializer = InstitutionSerializer(institution, data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(qs=obj.tags.all(),
                                 values=["blabla", "X", "Z"],
                                 transform=force_text)
        self.assertEqual(Institution.objects.count(), 1)  # updated


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


class SitemapTestCase(ObjectMixin, TestCase):
    def test_institutions(self):
        url = reverse('sitemaps', kwargs={'section': 'institutions'})
        needle = reverse('institutions:details', kwargs={'slug': self.institution})
        response = self.client.get(url)
        self.assertContains(response, needle)

    def test_tags(self):
        tag_used = TagFactory()
        institution = InstitutionFactory()
        institution.tags.add(tag_used)
        institution.save()
        tag_free = TagFactory()
        url = reverse('sitemaps', kwargs={'section': 'institutions_tags'})
        response = self.client.get(url)
        self.assertContains(response, tag_used.get_absolute_url())
        self.assertNotContains(response, tag_free.get_absolute_url())
