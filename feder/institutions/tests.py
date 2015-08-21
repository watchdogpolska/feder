from django.test import TestCase

# Create your tests here.
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from feder.teryt.models import JednostkaAdministracyjna
from feder.institutions.models import Institution
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import assign_perm
from . import views

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class InstitutionTestCase(TestCase):
    def _get_third_level_jst(self):
        jst = JednostkaAdministracyjna(name="ZXXC")
        jst.save()
        jst = JednostkaAdministracyjna(name="ZZZ", parent=jst)
        jst.save()
        jst = JednostkaAdministracyjna(name="ZZZZ", parent=jst)
        jst.save()
        JednostkaAdministracyjna.objects.rebuild()
        return jst

    def _assing_all_perm(self, user):
        assign_perm('institution.add_institution', self.user)
        assign_perm('institution.change_institution', self.user)
        assign_perm('institution.update_institution', self.user)

    def _get_institution(self):
        jst = self._get_third_level_jst()
        institution = Institution(name="Ins", email="X@example.com", user=self.user, jst=jst)
        institution.save()
        return institution

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        self._assign_all_perm(self.user)
        self.quest = User.objects.create_user(
            username='smith', email='smith@example.com', password='top_secret')
        self._get_institution()

    def test_details_display(self):
        request = self.factory.get(self.institution.get_absolute_url())
        request.user = self.user
        response = views.InstitutionDetailView.as_view()(request, slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)

    def test_create_permission_check(self):
        request = self.factory.get(reverse('institutions:create'))
        request.user = self.user
        response = views.InstitutionCreateView.as_view()(request, slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        with self.assertRaises(PermissionDenied):
            views.InstitutionCreateView.as_view()(request, slug=self.institution.slug)

    def test_update_permission_check(self):
        request = self.factory.get(reverse('institutions:update',
            kwargs={'slug': self.institution.slug}))
        request.user = self.user
        response = views.InstitutionUpdateView.as_view()(request, slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        with self.assertRaises(PermissionDenied):
            views.InstitutionUpdateView.as_view()(request, slug=self.institution.slug)

    def test_delete_permission_check(self):
        request = self.factory.get(reverse('institutions:delete',
            kwargs={'slug': self.institution.slug}))
        request.user = self.user
        response = views.InstitutionDeleteView.as_view()(request, slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        with self.assertRaises(PermissionDenied):
            views.InstitutionDeleteView.as_view()(request, slug=self.institution.slug)
