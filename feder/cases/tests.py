from django.urls import reverse
from django.test import RequestFactory, TestCase

from feder.cases.models import Case
from feder.institutions.factories import InstitutionFactory
from feder.letters.factories import IncomingLetterFactory
from feder.letters.models import Letter
from feder.main.tests import PermissionStatusMixin
from feder.parcels.factories import IncomingParcelPostFactory
from feder.users.factories import UserFactory
from .factories import CaseFactory, AliasFactory
from .forms import CaseForm
from .views import CaseAutocomplete
from feder.teryt.factories import JSTFactory, CommunityJSTFactory, CountyJSTFactory


class ObjectMixin:
    def setUp(self):
        self.user = UserFactory(username="john")
        self.case = CaseFactory()
        self.permission_object = self.case.monitoring


class CaseFormTestCase(ObjectMixin, TestCase):
    def test_standard_save(self):
        data = {"name": "example", "institution": InstitutionFactory().pk}
        form = CaseForm(monitoring=self.case.monitoring, user=self.user, data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        obj = form.save()
        self.assertEqual(obj.name, "example")
        self.assertEqual(obj.monitoring, self.case.monitoring)
        self.assertEqual(obj.user, self.user)


class CaseListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("cases:list")

    def test_for_filter_cases_by_community(self):
        common_county = CountyJSTFactory()
        valid = CaseFactory(institution__jst=CommunityJSTFactory(parent=common_county))
        invalid = CaseFactory(
            institution__jst=CommunityJSTFactory(parent=common_county)
        )
        response = self.client.get(
            "{}?voideship={}&county={}&community={}".format(
                self.get_url(),
                common_county.parent.pk,
                common_county.pk,
                valid.institution.jst.pk,
            )
        )
        self.assertContains(response, valid.name)
        self.assertContains(response, valid.institution.name)
        self.assertNotContains(response, invalid.name)
        self.assertNotContains(response, invalid.institution.name)


class CaseDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse("cases:details", kwargs={"slug": self.case.slug})

    def test_show_note_on_letter(self):
        letter = IncomingLetterFactory(record__case=self.case)
        response = self.client.get(self.get_url())
        self.assertContains(response, letter.note)

    def test_not_contains_spam_letter(self):
        letter = IncomingLetterFactory(record__case=self.case, is_spam=Letter.SPAM.spam)
        response = self.client.get(self.get_url())
        self.assertNotContains(response, letter.body)

    def test_contains_letter(self):
        letter = IncomingLetterFactory(record__case=self.case)
        response = self.client.get(self.get_url())
        self.assertContains(response, letter.body)

    def test_show_parce_post(self):
        parcel = IncomingParcelPostFactory(record__case=self.case)
        response = self.client.get(self.get_url())
        self.assertContains(response, parcel.title)


class CaseCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.add_case"]

    def get_url(self):
        return reverse(
            "cases:create", kwargs={"monitoring": str(self.case.monitoring.pk)}
        )


class CaseUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_case"]

    def get_url(self):
        return reverse("cases:update", kwargs={"slug": self.case.slug})


class CaseDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.delete_case"]

    def get_url(self):
        return reverse("cases:delete", kwargs={"slug": self.case.slug})


class CaseAutocompleteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_by_name(self):
        CaseFactory(name="123")
        CaseFactory(name="456")
        request = self.factory.get("/customer/details", data={"q": "123"})
        response = CaseAutocomplete.as_view()(request)
        self.assertContains(response, "123")
        self.assertNotContains(response, "456")


class SitemapTestCase(ObjectMixin, TestCase):
    def test_cases(self):
        url = reverse("sitemaps", kwargs={"section": "cases"})
        needle = reverse("cases:details", kwargs={"slug": self.case.slug})
        response = self.client.get(url)
        self.assertContains(response, needle)


class CaseQuerySetTestCase(TestCase):
    def test_find_by_email(self):
        case = CaseFactory(email="case-123@example.com")

        self.assertEqual(
            Case.objects.by_addresses(["case-123@example.com"]).get(), case
        )

    def test_find_by_alias(self):
        case = CaseFactory(email="case-123@example.com")
        AliasFactory(case=case, email="alias-123@example.com")

        self.assertEqual(
            Case.objects.by_addresses(["alias-123@example.com"]).get(), case
        )
