from django.core.urlresolvers import reverse
from django.test import TestCase

from feder.main.mixins import PermissionStatusMixin
from feder.tasks.factories import (CharAnswerFactory, JSTAnswerFactory,
                                   SurveyFactory)
from feder.teryt.factories import JSTFactory
from .test_general import ObjectMixin
from ..factories import CharQuestionFactory, JSTQuestionFactory
from ..models import Questionary


class QuestionaryCreateTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.add_questionary', ]

    def get_url(self):
        return reverse('questionaries:create',
                       kwargs={'monitoring': str(self.questionary.monitoring.pk)})


class QuestionaryListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
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
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return self.questionary.get_absolute_url()

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questionaries/questionary_detail.html')
        self.assertContains(response, self.questionary.title)


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

    def test_get_success_url(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.post(self.get_url())
        self.assertFalse(Questionary.objects.filter(pk=self.questionary.pk).exists())
        self.assertRedirects(response,
                             self.questionary.monitoring.get_absolute_url())


class SitemapTestCase(ObjectMixin, TestCase):
    def test_institutions(self):
        url = reverse('sitemaps', kwargs={'section': 'questionaries'})
        response = self.client.get(url)
        self.assertContains(response, self.questionary.get_absolute_url())


class SurveyCSVViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = []
    status_anonymous = 200
    status_no_permission = 200

    def get_url(self):
        return reverse('questionaries:export',
                       kwargs={'pk': self.questionary.pk})

    def test_no_question(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_no_answer_but_has_questions(self):
        char_q = CharQuestionFactory(questionary=self.questionary)
        jst_q = JSTQuestionFactory(questionary=self.questionary)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, char_q.definition['name'])
        self.assertContains(response, jst_q.definition['name'])

    def test_save_answer(self):
        survey = SurveyFactory(task__questionary=self.questionary)
        char_a = CharAnswerFactory(survey=survey)
        jst = JSTFactory()
        JSTAnswerFactory(survey=survey, value=jst.pk)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, char_a.content['value'])
        self.assertContains(response, jst.name)
