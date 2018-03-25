from django.urls import reverse
from django.template import Context
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.main.mixins import PermissionStatusMixin
from .test_general import ObjectMixin
from ..factories import CharQuestionFactory
from ..forms import QuestionForm, QuestionDefinitionForm
from ..models import Question

try:
    from django.template.loader import get_template_from_string
except ImportError:
    from django.template import Engine

    get_template_from_string = Engine.get_default().from_string


def render_form(form):
    template = get_template_from_string("""
        {% load crispy_forms_tags %}
        {% crispy form %}
    """)
    c = Context({'form': form})
    return template.render(c)


class QuestionObjectMixin(ObjectMixin):
    def setUp(self):
        super(QuestionObjectMixin, (self)).setUp()
        self.question = CharQuestionFactory(questionary=self.questionary,
                                            position=0)


class QuestionFormTestCase(ObjectMixin, TestCase):
    def test_construct_form(self):
        form = QuestionForm(questionary=self.questionary)
        html = render_form(form)
        self.assertIn('input', html)
        self.assertSequenceEqual(sorted(form.fields.keys()),
                                 sorted(['position', 'genre']))


class QuestionDefinitionFormTestCase(QuestionObjectMixin, TestCase):
    def test_construct_form(self):
        form = QuestionDefinitionForm(user=self.user,
                                      instance=self.question)
        html = render_form(form)
        self.assertIn('input', html)
        self.assertSequenceEqual(sorted(form.fields.keys()),
                                 sorted(['name', 'help_text', 'required',
                                         'comment', 'comment_label',
                                         'comment_help', 'comment_required']))

    def test_save(self):
        self.question.definition = {}
        self.question.save()
        form = QuestionDefinitionForm(user=self.user,
                                      instance=self.question,
                                      data={'name': 'Foo bar',
                                            'help_text': 'Foo'})
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.save(), Question)
        self.assertNotEqual(self.question.definition, {})
        self.assertEqual(self.question.definition['comment'], False)
        self.assertEqual(self.question.definition['name'], 'Foo bar')
        self.assertEqual(self.question.definition['required'], False)
        self.assertEqual(self.question.definition['comment_required'], False)
        self.assertEqual(self.question.definition['comment_label'], '')
        self.assertEqual(self.question.definition['comment_help'], '')
        self.assertEqual(self.question.definition['help_text'], 'Foo')


class QuestionCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_questionary', ]

    def get_url(self):
        return reverse('questionaries:question_create',
                       kwargs={'pk': self.questionary.pk})


class QuestionMoveViewTestCase(QuestionObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitoring.change_questionary', ]

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


class QuestionDeleteViewTestCase(QuestionObjectMixin, PermissionStatusMixin, TestCase):
    permission = ['monitorings.change_questionary', ]

    def get_url(self):
        return reverse('questionaries:question_delete',
                       kwargs={'pk': self.question.pk})

    def test_get_success_url(self):
        self.grant_permission()
        self.client.login(username='john', password='pass')
        response = self.client.post(self.get_url())
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())
        self.assertRedirects(response,
                             self.questionary.get_absolute_url())
