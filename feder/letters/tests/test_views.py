from __future__ import absolute_import, unicode_literals

import os
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.alerts.models import Alert
from feder.cases.factories import CaseFactory
from feder.letters.models import Letter
from feder.letters.tests.base import MessageMixin
from feder.main.mixins import PermissionStatusMixin
from feder.monitorings.factories import MonitoringFactory
from feder.records.models import Record
from feder.users.factories import UserFactory
from ..factories import IncomingLetterFactory, OutgoingLetterFactory, AttachmentFactory, LetterFactory
from django.utils.translation import ugettext_lazy as _


class ObjectMixin(object):
    def setUp(self):
        super(ObjectMixin, self).setUp()
        self.user = UserFactory(username='john')
        self.monitoring = self.permission_object = MonitoringFactory()
        self.case = CaseFactory(monitoring=self.monitoring)
        self.from_user = OutgoingLetterFactory(title='Wniosek',
                                               record__case=self.case)

        self.letter = self.from_institution = IncomingLetterFactory(title='Odpowiedz',
                                                                    record__case=self.case)


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

    def test_contains_link_to_attachment(self):
        attachment = AttachmentFactory(letter=self.letter)
        response = self.client.get(self.get_url())
        self.assertContains(response, attachment.get_absolute_url())


class LetterMessageXSendFileView(PermissionStatusMixin, TestCase):
    permission = []
    status_has_permission = 200
    status_anonymous = 200
    status_no_permission = 200

    def setUp(self):
        super(LetterMessageXSendFileView, self).setUp()
        self.object = IncomingLetterFactory(is_spam=Letter.SPAM.non_spam)

    def get_url(self):
        return reverse('letters:download', kwargs={'pk': self.object.pk})

    def test_deny_access_for_spam(self):
        spam_obj = IncomingLetterFactory(is_spam=Letter.SPAM.spam)
        url = reverse('letters:download', kwargs={'pk': spam_obj.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class LetterCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_letter', ]

    def get_url(self):
        return reverse('letters:create', kwargs={'case_pk': self.case.pk})


class LetterUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_letter', ]

    def get_url(self):
        return reverse('letters:update', kwargs={'pk': self.from_user.pk})

    def test_update_case_number(self):
        self.login_permitted_user()
        new_case = CaseFactory()
        self.assertNotEqual(self.from_user.case, new_case)
        data = {'title': 'Lorem',
                'body': 'Lorem',
                'case': new_case.pk,
                'attachment_set-TOTAL_FORMS': 0,
                'attachment_set-INITIAL_FORMS': 0,
                'attachment_set-MAX_NUM_FORMS': 1}
        resp = self.client.post(self.get_url(), data)
        self.assertEqual(resp.status_code, 302)
        self.from_user.refresh_from_db()
        self.from_user.record.refresh_from_db()
        self.assertEqual(self.from_user.case, new_case)


class LetterDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_letter', ]

    def get_url(self):
        return reverse('letters:delete', kwargs={'pk': self.from_user.pk})

    def test_remove_eml_file(self):
        self.login_permitted_user()
        self.assertTrue(os.path.isfile(self.from_user.eml.file.name))
        self.client.post(self.get_url())
        self.assertFalse(os.path.isfile(self.from_user.eml.file.name))


class LetterReplyViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.reply', 'monitorings.add_draft']

    def get_url(self):
        return reverse('letters:reply', kwargs={'pk': self.from_institution.pk})

    def test_send_reply(self):
        self.login_permitted_user()
        simple_file = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
        response = self.client.post(self.get_url(),
                                    {'body': 'Lorem',
                                     'title': 'Lorem',
                                     'send': 'yes',
                                     'attachment_set-TOTAL_FORMS': 1,
                                     'attachment_set-INITIAL_FORMS': 0,
                                     'attachment_set-MAX_NUM_FORMS': 1,
                                     'attachment_set-0-attachment': simple_file},
                                    format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        new_letter = Letter.objects.filter(title="Lorem").get()
        new_attachment = new_letter.attachment_set.get()
        self.assertIn(new_attachment.get_full_url(), mail.outbox[0].body)
        self.assertEqual(Record.objects.count(), 3)

    def test_no_send_drafts(self):
        self.login_permitted_user()
        response = self.client.post(self.get_url(),
                                    {'body': 'Lorem',
                                     'title': 'Lorem',
                                     'attachment_set-TOTAL_FORMS': 0,
                                     'attachment_set-INITIAL_FORMS': 0,
                                     'attachment_set-MAX_NUM_FORMS': 1
                                     })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)


class LetterSendViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.reply', ]

    def get_url(self):
        return reverse('letters:send', kwargs={'pk': self.from_user.pk})

    def test_send_reply(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.post(self.get_url())
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


class LetterReportSpamViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse('letters:spam', kwargs={'pk': self.from_institution.pk})

    def test_create_report_for_anonymous(self):
        response = self.client.post(self.get_url())
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.get()
        self.assertEqual(alert.link_object, self.from_institution)
        self.assertEqual(alert.author, None)

    def test_create_report_for_user(self):
        self.client.login(username='john', password='pass')
        response = self.client.post(self.get_url())
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.get()
        self.assertEqual(alert.link_object, self.from_institution)
        self.assertEqual(alert.author, self.user)


class LetterMarkSpamViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.spam_mark', ]

    def get_url(self):
        return reverse('letters:mark_spam', kwargs={'pk': self.from_institution.pk})

    def test_hide_by_staff(self):
        self.login_permitted_user()
        response = self.client.post(self.get_url())
        self.from_institution = Letter.objects_with_spam.get(pk=self.from_institution.pk)
        self.assertEqual(self.from_institution.is_spam, Letter.SPAM.spam)

    def test_mark_as_valid(self):
        self.login_permitted_user()
        response = self.client.post(self.get_url(), data={'valid': 'x'})
        self.from_institution.refresh_from_db()
        self.assertEqual(self.from_institution.is_spam, Letter.SPAM.non_spam)

    def test_accept_global_perms(self):
        user = UserFactory()
        assign_perm('monitorings.spam_mark', user)
        self.client.login(username=user.username, password='pass')

        response = self.client.post(self.get_url(), data={'valid': 'x'})
        self.from_institution.refresh_from_db()
        self.assertEqual(self.from_institution.is_spam, Letter.SPAM.non_spam)


class MessageObjectMixin(object):
    def setUp(self):
        super(MessageObjectMixin, self).setUp()
        self.user = UserFactory(username='john')
        self.monitoring = MonitoringFactory()
        self.case = CaseFactory(monitoring=self.monitoring)


class UnrecognizedMessageListViewTestView(MessageObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['letters.recognize_letter']
    permission_object = None

    def get_url(self):
        return reverse('letters:messages_list')


class AssignMessageFormViewTestCase(MessageMixin, MessageObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['letters.recognize_letter']

    def setUp(self):
        super(AssignMessageFormViewTestCase, self).setUp()
        self.user = UserFactory(username='john')
        self.msg = self.get_message('basic_message.eml')

    def get_url(self):
        return reverse('letters:messages_assign', kwargs={'pk': self.msg.pk})

    def test_assign_simple_letter(self):
        self.client.login(username=UserFactory(is_superuser=True).username,
                          password='pass')
        self.case = CaseFactory()
        response = self.client.post(self.get_url(), data={'case': self.case.pk})
        self.assertRedirects(response, reverse('letters:messages_list'))
        self.assertTrue(self.msg.letter_set.exists())


class SpamAttachmentXSendFileViewTestCase(PermissionStatusMixin, TestCase):
    permission = []
    status_has_permission = 404
    status_anonymous = 404
    status_no_permission = 404
    spam_status = Letter.SPAM.spam

    def setUp(self):
        super(SpamAttachmentXSendFileViewTestCase, self).setUp()
        self.object = AttachmentFactory(letter__is_spam=self.spam_status)

    def get_url(self):
        return reverse('letters:attachment', kwargs={'pk': self.object.pk, 'letter_pk': 0})


class StandardAttachmentXSendFileViewTestCase(PermissionStatusMixin, TestCase):
    permission = []
    status_has_permission = 200
    status_anonymous = 200
    status_no_permission = 200
    spam_status = Letter.SPAM.non_spam

    def setUp(self):
        super(StandardAttachmentXSendFileViewTestCase, self).setUp()
        self.object = AttachmentFactory(letter__is_spam=self.spam_status)

    def get_url(self):
        return reverse('letters:attachment', kwargs={'pk': self.object.pk, 'letter_pk': 0})
