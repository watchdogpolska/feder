from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from feder.teryt.models import JednostkaAdministracyjna
from feder.institutions.models import Institution
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import assign_perm
from autofixture import AutoFixture
from feder.institutions import views

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class InstitutionTestCase(TestCase):
    def _get_third_level_jst(self):
        jst = AutoFixture(JednostkaAdministracyjna,
            field_values={'updated_on': '2015-02-12'},
            generate_fk=True).create_one(commit=False)
        jst.rght = 0
        jst.save()
        JednostkaAdministracyjna.objects.rebuild()
        return jst

    @staticmethod
    def _assign_all_perm(user):
        assign_perm('institutions.add_institution', user)
        assign_perm('institutions.change_institution', user)
        assign_perm('institutions.delete_institution', user)

    def _get_institution(self):
        jst = self._get_third_level_jst()
        institution = AutoFixture(Institution,
            field_values={'user': self.user, 'jst': jst}).create_one()
        return institution

    def setUp(self):
        self.factory = RequestFactory()
        self.user = AutoFixture(User).create_one()
        self._assign_all_perm(self.user)
        self.quest = AutoFixture(User, field_values={'is_superuser': False}).create_one()
        self.institution = self._get_institution()

    def test_details_display(self):
        request = self.factory.get(self.institution.get_absolute_url())
        request.user = self.user
        response = views.InstitutionDetailView.as_view()(request, slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)

    def _perm_check(self, view, reverse_name, kwargs):
        request = self.factory.get(reverse(reverse_name,
            kwargs=kwargs))
        request.user = self.user
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)

        request.user = self.quest
        with self.assertRaises(PermissionDenied):
            view(request, **kwargs)

    def test_create_permission_check(self):
        self._perm_check(views.InstitutionCreateView.as_view(), 'institutions:create', kwargs={})

    def test_update_permission_check(self):
        self._perm_check(views.InstitutionUpdateView.as_view(), 'institutions:update',
            kwargs={'slug': self.institution.slug})

    def test_delete_permission_check(self):
        self._perm_check(views.InstitutionDeleteView.as_view(), 'institutions:delete',
            kwargs={'slug': self.institution.slug})
