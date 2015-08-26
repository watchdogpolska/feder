from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from feder.monitorings.models import Monitoring
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import assign_perm
from autofixture import AutoFixture
# from feder.teryt.models import JednostkaAdministracyjna
# from feder.institutions.models import Institution
from feder.questionaries import views
from feder.questionaries.models import Questionary

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class QuestionariesTestCase(TestCase):
    # def _get_third_level_jst(self):
    #     jst = AutoFixture(JednostkaAdministracyjna,
    #         field_values={'updated_on': '2015-02-12'},
    #         generate_fk=True).create_one(commit=False)
    #     jst.save()
    #     JednostkaAdministracyjna.objects.rebuild()
    #     return jst

    # def _get_institution(self):
    #     self._get_third_level_jst()
    #     institution = AutoFixture(Institution,
    #         field_values={'user': self.user},
    #         generate_fk=True).create_one()
    #     return institution

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        assign_perm('monitorings.add_monitoring', self.user)
        self.quest = User.objects.create_user(
            username='smith', email='smith@example.com', password='top_secret')
        self.monitoring = Monitoring(name="Lor", user=self.user)
        self.monitoring.save()
        self.questionary = Questionary(title="blabla", monitoring=self.monitoring)
        self.questionary.save()

    def test_list_display(self):
        response = self.client.get(reverse('questionaries:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/questionary_filter.html')
        self.assertContains(response, self.questionary.title)

    def test_details_display(self):
        response = self.client.get(self.questionary.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/questionary_detail.html')
        self.assertContains(response, self.questionary.title)

    def _perm_check(self, url, template_name='questionaries/questionary_form.html', contains=True):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='jacob', password='top_secret')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        if contains:
            self.assertContains(response, self.questionary.title)

    def test_create_permission_check(self):
        self._perm_check(reverse('questionaries:create',
                                 kwargs={'monitoring': str(self.monitoring.pk)}),
                         contains=False)

    def test_update_permission_check(self):
        self._perm_check(reverse('questionaries:update',
                                 kwargs={'pk': self.questionary.pk}))

    def test_delete_permission_check(self):
        self._perm_check(reverse('questionaries:delete',
                                 kwargs={'pk': self.questionary.pk}),
                         template_name='questionaries/questionary_confirm_delete.html')

    def test_delete_post(self):
        url = reverse('questionaries:delete', kwargs={'pk': self.questionary.pk})
        self.assertTrue(Questionary.objects.filter(pk=self.questionary.pk).exists())
        self.client.login(username='jacob', password='top_secret')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, self.monitoring.get_absolute_url())
        self.assertFalse(Questionary.objects.filter(pk=self.questionary.pk).exists())
