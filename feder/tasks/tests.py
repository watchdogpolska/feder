from django.urls import reverse
from django.test import TestCase
from django.utils.encoding import force_text

from feder.main.tests import PermissionStatusMixin
from feder.questionaries.factories import (
    CharQuestionFactory,
    JSTQuestionFactory,
    QuestionaryFactory,
)
from feder.teryt.factories import JSTFactory
from feder.users.factories import UserFactory
from .factories import TaskFactory
from .models import Answer, Survey


class ObjectMixin:
    def setUp(self):
        self.user = UserFactory(username="john")
        self.task = TaskFactory()
        self.permission_object = self.task.case.monitoring


class TaskTestCase(ObjectMixin, TestCase):
    def test_list_display(self):
        response = self.client.get(reverse("tasks:list"))
        self.assertEqual(response.status_code, 200)

    def test_details_display(self):
        response = self.client.get(self.task.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class TaskCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.add_task"]

    def get_url(self):
        return reverse("tasks:create", kwargs={"case": str(self.task.case.pk)})


class TaskUpdateViewPermTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_task"]

    def get_url(self):
        return reverse("tasks:update", kwargs={"pk": self.task.pk})


class TaskDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.delete_task"]
    template_name = "tasks/task_confirm_delete.html"

    def get_url(self):
        return reverse("tasks:delete", kwargs={"pk": self.task.pk})


class SurveyFillViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_no_permission = 200
    status_anonymous = 200

    permission = []

    def setUp(self):
        self.user = UserFactory(username="john", password="pass")
        self.questionary = QuestionaryFactory()
        self.question_char = CharQuestionFactory(
            questionary=self.questionary, comment=True
        )
        self.question_jst = JSTQuestionFactory(questionary=self.questionary)
        self.task = TaskFactory(questionary=self.questionary)

    def get_url(self):
        return reverse("tasks:fill_survey", kwargs={"pk": self.task.pk})

    def test_display_form(self):
        self.client.login(username="john", password="pass")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "%s-value" % (self.question_char.pk)
        )  # contains formset

    def test_save_new_survey(self):
        self.assertEqual(Survey.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)
        self.client.login(username="john", password="pass")
        q_id = self.question_char.pk
        q2_id = self.question_jst.pk
        jst = JSTFactory()
        response = self.client.post(
            self.get_url(),
            data={
                ("%s-value" % (q_id)): "foo-uniq-1",
                ("%s-comment" % (q_id)): "foo-uniq-2",
                ("%s-value" % (q2_id)): jst.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 2)
        answer_char = Answer.objects.get(question=self.question_char)
        answer_jst = Answer.objects.get(question=self.question_jst)
        self.assertIn("foo-uniq-1", force_text(answer_char.content))
        self.assertIn("foo-uniq-2", force_text(answer_char.content))
        self.assertIn(str(jst.pk), force_text(answer_jst.content))

    def test_validation_failing(self):
        self.client.login(username="john", password="pass")
        q_id = self.question_char.pk
        response = self.client.post(
            self.get_url(),
            data={("%s-value" % (q_id)): "", ("%s-comment" % (q_id)): "foo-uniq-2"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "foo-uniq-2")
        self.assertContains(
            response, "%s-value" % (self.question_char.pk)
        )  # contains formset


class SitemapTestCase(ObjectMixin, TestCase):
    def test_letters(self):
        url = reverse("sitemaps", kwargs={"section": "tasks"})
        response = self.client.get(url)
        self.assertContains(response, self.task.get_absolute_url())
