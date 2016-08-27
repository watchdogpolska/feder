from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.main.mixins import PermissionStatusMixin
from feder.monitorings.models import Monitoring
from feder.questionaries.models import Question, Questionary
from feder.users.factories import UserFactory

from .factories import QuestionaryFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john',)
        self.questionary = QuestionaryFactory()
        self.permission_object = self.questionary.monitoring


class QuestionaryListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('questionaries:list')

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/questionary_filter.html')
        self.assertContains(response, self.questionary.title)


class QuestionaryDetailsViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return self.questionary.get_absolute_url()

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/questionary_detail.html')
        self.assertContains(response, self.questionary.title)


class QuestionaryCreateTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_questionary', ]

    def get_url(self):
        return reverse('questionaries:create',
                       kwargs={'monitoring': str(self.questionary.monitoring.pk)})


class QuestionaryUpdateTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_questionary', ]

    def get_url(self):
        return reverse('questionaries:update',
                       kwargs={'pk': self.questionary.pk})


class QuestionaryDeleteTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.delete_questionary', ]

    def get_url(self):
        return reverse('questionaries:delete',
                       kwargs={'pk': self.questionary.pk})


class QuestionaryQuestionCreateTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_questionary', ]

    def get_url(self):
        return reverse('questionaries:question_create',
                       kwargs={'pk': self.questionary.pk})


class QuestionWizardTestCase(ObjectMixin, TestCase):  # TODO: Add PermissionStatusMixin
    def get_url(self):
        return reverse('questionaries:question_create', kwargs={'pk': self.questionary.pk})

    def test_question_step1(self):  # TODO: Add lock test
        assign_perm('monitoring.change_questionary', self.user, self.permission_object)
        self.client.login(username='john', password='pass')
        self.client.get(self.get_url())
        response = self.client.post(self.get_url(), {'question_wizard-current_step': '0',
                                                     '0-position': '2',
                                                     '0-genre': 'char',
                                                     'submit': 'y'})
        self.assertEqual(response.status_code, 200)

    def test_question_step2(self):
        assign_perm('monitoring.change_questionary', self.user, self.permission_object)
        self.client.login(username='john', password='pass')

        self.client.post(self.get_url(), {'question_wizard-current_step': '0',
                                          '0-position': '2',
                                          '0-genre': 'char',
                                          'submit': 'y'})  # Submit first step

        response = self.client.post(self.get_url(), {'question_wizard-current_step': '1',
                                                     '1-name': 'Question name',
                                                     '1-help_text': 'Question help_text',
                                                     '1-required': 'on',
                                                     'submit': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 1)


class QuestionMoveViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitoring.change_questionary', ]

    def setUp(self):
        super(QuestionMoveViewTestCase, (self)).setUp()
        blob = {'help_text': 'Question help_text',
                'required': True,
                'name': 'Question name'}
        self.question = Question.objects.create(questionary=self.questionary,
                                                position=0,
                                                genre='char',
                                                blob=blob)

    def get_url(self):
        return reverse('questionaries:question_down',
                       kwargs={'pk': self.question.pk})

    def test_question_move(self):
        assign_perm('monitoring.change_questionary', self.user, self.permission_object)
        self.client.login(username='john', password='pass')

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/question_move.html')

        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Question.objects.get(pk=self.question.pk).position, +1)
