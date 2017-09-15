from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.cases.models import Case
from feder.institutions.factories import InstitutionFactory
from feder.letters.factories import IncomingLetterFactory
from feder.letters.factories import OutgoingLetterFactory
from feder.main.mixins import PermissionStatusMixin
from feder.users.factories import UserFactory
from .factories import MonitoringFactory
from .forms import MonitoringForm
from .models import Monitoring

EXAMPLE_DATA = {'name': 'foo-bar-monitoring',
                'description': 'xyz',
                'notify_alert': True,
                'subject': 'example subject',
                'template': 'xyz {{EMAIL}}'}


class MonitoringFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(username="john")

    def test_form_save_user(self):
        form = MonitoringForm(EXAMPLE_DATA.copy(), user=self.user)
        self.assertTrue(form.is_valid(), msg=form.errors)
        obj = form.save()
        self.assertEqual(obj.user, self.user)

    def test_form_template_validator(self):
        data = EXAMPLE_DATA.copy()
        data['template'] = 'xyzyyz'
        form = MonitoringForm(data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('template', form.errors)


class ObjectMixin(object):
    def setUp(self):
        super(ObjectMixin, (self)).setUp()
        self.user = UserFactory(username="john")
        self.monitoring = self.permission_object = MonitoringFactory(subject="Wniosek")


class MonitoringCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse('monitorings:create')
    permission = ['monitorings.add_monitoring', ]

    def get_permission_object(self):
        return None

    def test_template_used(self):
        assign_perm('monitorings.add_monitoring', self.user)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")

    def test_assign_perm_for_creator(self):
        assign_perm('monitorings.add_monitoring', self.user)
        self.client.login(username='john', password='pass')
        data = EXAMPLE_DATA.copy()
        response = self.client.post(self.get_url(), data=data)
        self.assertEqual(response.status_code, 302)
        monitoring = Monitoring.objects.get(name='foo-bar-monitoring')
        self.assertTrue(self.user.has_perm('monitorings.reply', monitoring))


class MonitoringListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('monitorings:list')

    def test_list_display(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)


class MonitoringDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return self.monitoring.get_absolute_url()

    def test_details_display(self):
        response = self.client.get(self.get_url())
        self.assertContains(response, self.monitoring)


class LetterListMonitoringViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('monitorings:letters', kwargs={'slug': self.monitoring})

    def test_list_display(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_display_letter(self):
        letter = IncomingLetterFactory(case__monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertContains(response, letter.body)
        self.assertContains(response, letter.note)


class DraftListMonitoringViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('monitorings:drafts', kwargs={'slug': self.monitoring})

    def test_list_display(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_display_draft(self):
        draft_letter = OutgoingLetterFactory(case__monitoring=self.monitoring)
        incoming_letter = IncomingLetterFactory(case__monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertContains(response, draft_letter.body)
        self.assertContains(response, draft_letter.note)
        self.assertNotContains(response, incoming_letter.body)

class MonitoringUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_monitoring', ]

    def get_url(self):
        return reverse('monitorings:update', kwargs={'slug': self.monitoring.slug})

    def test_template_used(self):
        assign_perm('monitorings.change_monitoring', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")


class MonitoringDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_monitoring', ]

    def get_url(self):
        return reverse('monitorings:delete', kwargs={'slug': self.monitoring.slug})

    def test_template_used(self):
        assign_perm('monitorings.delete_monitoring', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_confirm_delete.html")


class PermissionWizardTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.manage_perm', ]

    def get_url(self):
        return reverse('monitorings:perm-add', kwargs={'slug': self.monitoring.slug})

    def test_template_used(self):
        assign_perm('monitorings.manage_perm', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'monitorings/permission_wizard.html')


class MonitoringPermissionViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.manage_perm', ]

    def get_url(self):
        return reverse('monitorings:perm', kwargs={'slug': self.monitoring.slug})

    def test_template_used(self):
        assign_perm('monitorings.manage_perm', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'monitorings/monitoring_permissions.html')


class MonitoringUpdatePermissionViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.manage_perm', ]

    def get_url(self):
        return reverse('monitorings:perm-update', kwargs={'slug': self.monitoring.slug,
                                                          'user_pk': self.user.pk})

    def test_template_used(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'monitorings/monitoring_form.html')


class MonitoringAssignViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_monitoring', ]

    def get_url(self):
        return reverse('monitorings:assign', kwargs={'slug': self.monitoring.slug})

    def test_assign_display_institutions(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory()
        institution_2 = InstitutionFactory()
        response = self.client.get(self.get_url())
        self.assertContains(response, institution_1.name)
        self.assertContains(response, institution_2.name)

    def test_send_to_all(self):
        self.login_permitted_user()
        InstitutionFactory()
        InstitutionFactory()
        InstitutionFactory()
        self.client.post(self.get_url(), data={'all': 'yes'})
        self.assertEqual(len(mail.outbox), 3)

    def test_send_to_selected(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory()
        institution_2 = InstitutionFactory()
        InstitutionFactory()
        to_send_ids = [institution_1.pk, institution_2.pk]
        self.client.post(self.get_url(), data={'to_assign': to_send_ids})
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], institution_1.email)
        self.assertEqual(mail.outbox[1].to[0], institution_2.email)
        for x in (0, 1):
            self.assertEqual(mail.outbox[x].subject, "Wniosek")

    def test_constant_increment_local_id(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory()
        institution_2 = InstitutionFactory()
        institution_3 = InstitutionFactory()
        self.client.post(self.get_url(), data={'to_assign': [institution_1.pk]})
        self.assertEqual(len(mail.outbox), 1)

        self.assertTrue(Case.objects.latest().name.endswith(' #1'))

        self.client.post(self.get_url(), data={'to_assign': [institution_2.pk,
                                                             institution_3.pk]})
        self.assertEqual(len(mail.outbox), 3)
        self.assertTrue(institution_2.case_set.all()[0].name.endswith(' #2'))
        self.assertTrue(institution_3.case_set.all()[0].name.endswith(' #3'))

        for x in (0, 1, 2):
            self.assertEqual(mail.outbox[x].subject, "Wniosek")


class SitemapTestCase(ObjectMixin, TestCase):
    def test_monitorings(self):
        url = reverse('sitemaps', kwargs={'section': 'monitorings'})
        needle = reverse('monitorings:details', kwargs={'slug': self.monitoring})
        response = self.client.get(url)
        self.assertContains(response, needle)

    def test_monitorings_pages(self):
        url = reverse('sitemaps', kwargs={'section': 'monitorings_pages'})
        needle = reverse('monitorings:details', kwargs={'slug': self.monitoring,
                                                        'page': 1})
        response = self.client.get(url)
        self.assertContains(response, needle)
