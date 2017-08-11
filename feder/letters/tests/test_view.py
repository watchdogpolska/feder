from __future__ import absolute_import, unicode_literals

from django.core import mail
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from feder.alerts.models import Alert
from feder.cases.factories import CaseFactory
from feder.letters.models import Letter
from feder.main.mixins import PermissionStatusMixin
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from ..factories import IncomingLetterFactory, OutgoingLetterFactory
from django.utils.translation import ugettext_lazy as _


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.monitoring = self.permission_object = MonitoringFactory()
        self.case = CaseFactory(monitoring=self.monitoring)
        self.from_user = OutgoingLetterFactory(title='Wniosek',
                                               case=self.case)

        self.letter = self.from_institution = IncomingLetterFactory(title='Odpowiedz',
                                                                    case=self.case)


class LetterListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:list')

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, 'letters/letter_filter.html')
        self.assertContains(response, 'Odpowiedz')
        self.assertContains(response, 'Wniosek')


class LetterDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return self.letter.get_absolute_url()

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'letters/letter_detail.html')
        self.assertContains(response, self.letter.title)

    def test_show_note(self):
        response = self.client.get(self.get_url())
        self.assertContains(response, self.letter.note)

    def test_contains_link_to_report_spam(self):
        response = self.client.get(self.get_url())
        self.assertContains(response, _("Report spam"))
        self.assertContains(response, reverse('letters:spam', kwargs={'pk': self.letter.pk}))


class LetterCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_letter', ]

    def get_url(self):
        return reverse('letters:create', kwargs={'case_pk': self.case.pk})


class LetterUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_letter', ]

    def get_url(self):
        return reverse('letters:update', kwargs={'pk': self.from_user.pk})


class LetterDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_letter', ]

    def get_url(self):
        return reverse('letters:delete', kwargs={'pk': self.from_user.pk})


class LetterReplyViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.reply', ]

    def get_url(self):
        return reverse('letters:reply', kwargs={'pk': self.from_institution.pk})

    def test_send_reply(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.post(self.get_url(),
                                    {'body': 'Lorem', 'title': 'Lorem', 'send': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)


class LetterRssFeedTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:rss')


class LetterAtomFeedTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:atom')

    def test_item_enclosure_url(self):
        self.from_institution.eml.save('msg.eml', ContentFile("Foo"), save=True)
        resp = self.client.get(self.get_url())
        self.assertContains(resp, self.from_institution.eml.name)


class LetterMonitoringRssFeedTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:rss', kwargs={'monitoring_pk': self.monitoring.pk})


class LetterMonitoringAtomFeedTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:rss', kwargs={'monitoring_pk': self.monitoring.pk})


class LetterCaseRssFeedTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:rss', kwargs={'case_pk': self.case.pk})


class LetterCaseAtomFeedTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:atom', kwargs={'case_pk': self.case.pk})


class SitemapTestCase(ObjectMixin, TestCase):
    def test_letters(self):
        url = reverse('sitemaps', kwargs={'section': 'letters'})
        needle = reverse('letters:details', kwargs={'pk': self.from_user.pk})
        response = self.client.get(url)
        self.assertContains(response, needle)


class ReportSpamViewTestCase (ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:spam', kwargs={'pk':  self.from_institution.pk})

    def test_create_report_for_anonymous(self):
        response = self.client.post(self.get_url())
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.get()
        self.assertEqual(alert.link_object, self.from_institution)

    def test_hide_by_admin(self):
        self.client.login(username=UserFactory(is_superuser=True).username,
                          password='pass')
        response = self.client.post(self.get_url())
        self.from_institution = Letter.objects_with_spam.get(pk=self.from_institution.pk)
        self.assertEqual(self.from_institution.is_spam, Letter.SPAM.spam)

    def test_mark_as_valid(self):
        self.client.login(username=UserFactory(is_superuser=True).username,
                          password='pass')
        response = self.client.post(self.get_url(), data={'valid': 'x'})
        self.from_institution.refresh_from_db()
        self.assertEqual(self.from_institution.is_spam, Letter.SPAM.non_spam)
