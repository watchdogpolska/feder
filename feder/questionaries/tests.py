from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.monitorings.models import Monitoring
from feder.questionaries.models import Question, Questionary
from feder.users.factories import UserFactory


class QuestionariesTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(username='john',)
        self.monitoring = Monitoring.objects.create(name="Lor",
                                                    user=self.user)
        self.questionary = Questionary.objects.create(title="blabla",
                                                      monitoring=self.monitoring)

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

    def _perm_check(self, url,
                    template_name='questionaries/questionary_form.html',
                    contains=True,
                    permission=None):
        permission = permission or []

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='john', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        for perm in permission:
            assign_perm(perm, self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        if contains:
            self.assertContains(response, self.questionary.title)

    def test_create_permission_check(self):
        self._perm_check(reverse('questionaries:create',
                                 kwargs={'monitoring': str(self.monitoring.pk)}),
                         contains=False,
                         permission=['monitorings.add_questionary', ])

    def test_update_permission_check(self):
        self._perm_check(reverse('questionaries:update',
                                 kwargs={'pk': self.questionary.pk}),
                         permission=['monitorings.change_questionary', ])

    def test_delete_permission_check(self):
        self._perm_check(reverse('questionaries:delete',
                                 kwargs={'pk': self.questionary.pk}),
                         template_name='questionaries/questionary_confirm_delete.html',
                         permission=['monitorings.delete_questionary', ])

    def test_question_create_permission_check(self):
        self._perm_check(reverse('questionaries:question_create',
                                 kwargs={'pk': self.questionary.pk}),
                         template_name='questionaries/question_wizard.html',
                         permission=['monitorings.change_questionary', ])

    def test_delete_post(self):
        assign_perm('monitoring.delete_questionary', self.user, self.monitoring)
        url = reverse('questionaries:delete', kwargs={'pk': self.questionary.pk})
        self.assertTrue(Questionary.objects.filter(pk=self.questionary.pk).exists())
        self.client.login(username='john', password='pass')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, self.monitoring.get_absolute_url())
        self.assertFalse(Questionary.objects.filter(pk=self.questionary.pk).exists())


class QuestionTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory(username='john')
        self.monitoring = Monitoring.objects.create(name="Lor", user=self.user)
        self.questionary = Questionary.objects.create(title="blabla", monitoring=self.monitoring)

    def test_question_create(self):  # TODO: Add lock test
        assign_perm('monitoring.change_questionary', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        url = reverse('questionaries:question_create', kwargs={'pk': self.questionary.pk})
        self.client.get(url)
        param = {'question_wizard-current_step': '0',
                 '0-position': '2',
                 '0-genre': 'char',
                 'submit': 'y'}
        response = self.client.post(url, param)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 1)
        response = self.client.post(url, {'question_wizard-current_step': '1',
                                          '1-name': 'Question name',
                                          '1-help_text': 'Question help_text',
                                          '1-required': 'on',
                                          'submit': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 2)


class QuestionTestCase(QuestionTestCase):

    def setUp(self):
        super(QuestionTestCase, self).setUp()
        blob = {'help_text': 'Question help_text', 'required': True, 'name': 'Question name'}
        self.question = Question.objects.create(questionary=self.questionary,
                                                position=0,
                                                genre='char',
                                                blob=blob)

    def _test_question_move(self, direction, target):
        assign_perm('monitoring.change_questionary', self.user, self.monitoring)
        self.client.login(username='john', password='pass')
        url = reverse('questionaries:question_' + direction,
                      kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/question_move.html')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Question.objects.get(pk=self.question.pk).position, target)

    def test_question_up(self):
        return self._test_question_move('up', -1)

    def test_question_down(self):
        return self._test_question_move('down', +1)
