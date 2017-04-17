from __future__ import absolute_import, unicode_literals

from django.core import mail
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from feder.cases.factories import CaseFactory
from feder.main.mixins import PermissionStatusMixin
from feder.monitorings.factories import MonitoringFactory
from feder.users.factories import UserFactory
from ..factories import IncomingLetterFactory, OutgoingLetterFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john')
        self.monitoring = self.permission_object = MonitoringFactory()
        self.case = CaseFactory(monitoring=self.monitoring)
        self.from_user = OutgoingLetterFactory(title='Wniosek',
                                               case=self.case)
        self.from_institution = IncomingLetterFactory(title='Odpowiedz',
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
        return self.from_user.get_absolute_url()

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'letters/letter_detail.html')
        self.assertContains(response, self.from_user.title)


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
