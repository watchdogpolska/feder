import json
from django.urls import reverse
from django.test import RequestFactory, TestCase
from django.utils.encoding import force_text
from guardian.shortcuts import assign_perm

from feder.main.tests import PermissionStatusMixin
from feder.teryt.factories import (
    JSTFactory,
    CountyJSTFactory,
    CommunityJSTFactory,
    VoivodeshipJSTFactory,
)
from feder.users.factories import UserFactory
from .factories import InstitutionFactory, TagFactory
from .models import Institution
from .serializers import InstitutionSerializer
from .views import InstitutionAutocomplete, TagAutocomplete


class InstitutionTestCase(TestCase):
    def _assign_community(self):
        self.voivodeship = VoivodeshipJSTFactory(name="Common voivodeship")
        self.county = CountyJSTFactory(parent=self.voivodeship, name="Common county")
        self.community = CommunityJSTFactory(
            parent=self.county, name="Common community"
        )

        self.obj.jst = self.community
        self.obj.save()

    def setUp(self):
        self.obj = InstitutionFactory(name="Example institution")

    def test_get_absolute_url(self):
        self.assertEqual(self.obj.get_absolute_url(), "/instytucje/example-institution")

    def test_get_str(self):
        self.assertEqual(force_text(self.obj), "Example institution")

    def test_get_voivodeship(self):
        # Third level JST
        self._assign_community()
        self.assertEqual(self.obj.voivodeship.name, "Common voivodeship")

        # Second level JST
        self.obj.jst = self.county
        self.obj.save()
        self.assertEqual(self.obj.voivodeship.name, "Common voivodeship")

        # First level JST
        self.obj.jst = self.voivodeship
        self.obj.save()
        self.assertEqual(self.obj.voivodeship.name, "Common voivodeship")

    def test_get_county(self):
        # Third level JST
        self._assign_community()
        self.assertEqual(self.obj.county.name, "Common county")

        # Second level JST
        self.obj.jst = self.county
        self.obj.save()
        self.assertEqual(self.obj.county.name, "Common county")

        # First level JST
        self.obj.jst = self.voivodeship
        self.obj.save()
        self.assertIsNone(self.obj.county)

    def test_get_community(self):
        # Third level JST
        self._assign_community()
        self.assertEqual(self.obj.community.name, "Common community")

        # Second level JST
        self.obj.jst = self.county
        self.obj.save()
        self.assertIsNone(self.obj.community)

        # First level JST
        self.obj.jst = self.voivodeship
        self.obj.save()
        self.assertIsNone(self.obj.community)


class InstitutionSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {
            "name": "xxx",
            "slug": "xxx",
            "tags": ["blabla", "X", "Z"],
            "regon": "0" * 14,
            "jst": JSTFactory().pk,
            "email": "example-2@example.com",
        }

    def test_create_institution(self):
        serializer = InstitutionSerializer(
            data={
                "name": "X",
                "email": "example-2@example.com",
                "regon": "0" * 14,
                "jst": JSTFactory().pk,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertTrue(serializer.save())

    def test_create_institution_with_tags(self):
        TagFactory(name="X")  # for colission tag name
        serializer = InstitutionSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(
            qs=obj.tags.all(), values=["blabla", "X", "Z"], transform=force_text
        )

    def test_update_institution_with_tags(self):
        institution = InstitutionFactory()

        self.data["pk"] = institution.pk

        serializer = InstitutionSerializer(institution, data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertQuerysetEqual(
            qs=obj.tags.all(), values=["blabla", "X", "Z"], transform=force_text
        )
        self.assertEqual(Institution.objects.count(), 1)  # updated


class ObjectMixin:
    def setUp(self):
        self.user = UserFactory(username="john")
        self.institution = InstitutionFactory()


class InstitutionListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse("institutions:list")
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "institutions/institution_filter.html")
        self.assertContains(response, self.institution.name)


class InstitutionDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return self.institution.get_absolute_url()

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "institutions/institution_detail.html")
        self.assertContains(response, self.institution.name)

    def test_can_view_edit_button_if_permitted(self):
        assign_perm("institutions.change_institution", self.user)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertContains(
            response,
            reverse("institutions:update", kwargs={"slug": self.institution.slug}),
        )


class InstitutionCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse("institutions:create")
    permission = ["institutions.add_institution"]


class InstitutionUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["institutions.change_institution"]

    def get_url(self):
        return reverse("institutions:update", kwargs={"slug": self.institution.slug})


class InstitutionDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["institutions.delete_institution"]

    def get_url(self):
        return reverse("institutions:delete", kwargs={"slug": self.institution.slug})


class InstitutionViewSetTestCase(ObjectMixin, TestCase):
    def test_csv_renderer(self):
        response = self.client.get("{}?format=csv".format(reverse("institution-list")))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["content-type"])
        self.assertContains(response, self.institution.name)


class InstitutionAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_by_name(self):
        InstitutionFactory(name="123")
        InstitutionFactory(name="456")
        request = self.factory.get("/customer/details", data={"q": "123"})
        response = InstitutionAutocomplete.as_view()(request)
        self.assertContains(response, "123")
        self.assertNotContains(response, "456")


class TagAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_by_name(self):
        TagFactory(name="123")
        TagFactory(name="456")
        request = self.factory.get("/customer/details", data={"q": "123"})
        response = TagAutocomplete.as_view()(request)
        self.assertContains(response, "123")
        self.assertNotContains(response, "456")

    def test_get_result_label_without_institution(self):
        TagFactory(name="123")
        request = self.factory.get("/customer/details", data={"q": "123"})
        response = TagAutocomplete.as_view()(request)
        self.assertContains(response, "123 (0)")

    def test_get_result_label_with_institution(self):
        institution = InstitutionFactory()
        institution.tags.add(TagFactory(name="123"))
        institution.save()

        request = self.factory.get("/customer/details", data={"q": "123"})
        response = TagAutocomplete.as_view()(request)
        self.assertContains(response, "123 (1)")

    def test_get_sorted_by_name(self):
        source_names = ["a2", "a3", "a1"]
        tags = [TagFactory(name=name) for name in source_names]
        [
            InstitutionFactory.create_batch(tags=[tag], size=count)
            for count, tag in enumerate(tags)
        ]
        request = self.factory.get("/customer/details")
        response = TagAutocomplete.as_view()(request)
        body = json.loads(response.content)

        expected_names = sorted(source_names)
        result_names = [x["text"].split(" ")[0] for x in body["results"]]

        self.assertListEqual(expected_names, result_names)


class SitemapTestCase(ObjectMixin, TestCase):
    def test_institutions(self):
        url = reverse("sitemaps", kwargs={"section": "institutions"})
        needle = reverse("institutions:details", kwargs={"slug": self.institution})
        response = self.client.get(url)
        self.assertContains(response, needle)

    def test_tags(self):
        tag_used = TagFactory()
        institution = InstitutionFactory()
        institution.tags.add(tag_used)
        institution.save()
        tag_free = TagFactory()
        url = reverse("sitemaps", kwargs={"section": "institutions_tags"})
        response = self.client.get(url)
        self.assertContains(response, tag_used.get_absolute_url())
        self.assertNotContains(response, tag_free.get_absolute_url())
