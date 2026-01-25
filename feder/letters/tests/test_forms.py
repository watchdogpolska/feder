from django.core import mail
from django.template import Context, Engine
from django.test import TestCase
from guardian.shortcuts import assign_perm

from feder.users.factories import UserFactory

from ..factories import IncomingLetterFactory
from ..forms import ReplyForm

get_template_from_string = Engine.get_default().from_string


def dict_merge(dict_a, *mergable):
    merged = dict_a.copy()
    [merged.update(x) for x in mergable]
    return merged


class ReplyFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(username="john")
        self.letter = IncomingLetterFactory()

    def render_form(self, form):
        template = get_template_from_string("""
            {% load crispy_forms_tags %}
            {% crispy form %}
        """)
        c = Context({"form": form})
        return template.render(c)

    def test_add_form_buttons_no_permission(self):
        form = ReplyForm(user=self.user, letter=self.letter)
        html = self.render_form(form)
        self.assertNotIn('name="save"', html)
        self.assertNotIn('name="send"', html)

    def test_add_form_buttons_with_permission(self):
        assign_perm("reply", self.user, self.letter.case.monitoring)
        assign_perm("add_draft", self.user, self.letter.case.monitoring)
        form = ReplyForm(user=self.user, letter=self.letter)
        html = self.render_form(form)
        self.assertIn('name="save"', html)
        self.assertIn('name="send"', html)

    def test_protected_at_all_without_permission(self):
        form = ReplyForm(user=self.user, letter=self.letter)
        self.assertEqual(form.is_valid(), False)

    def test_protected_sending(self):
        assign_perm("reply", self.user, self.letter.case.monitoring)
        data = {"body": "Lorem", "title": "Lorem", "save": "yes"}
        form = ReplyForm(user=self.user, letter=self.letter, data=data)
        self.assertEqual(form.is_valid(), False)

    def test_protected_repling(self):
        assign_perm("add_draft", self.user, self.letter.case.monitoring)
        data = {"body": "Lorem", "title": "Lorem", "send": "yes"}
        form = ReplyForm(user=self.user, letter=self.letter, data=data)
        self.assertEqual(form.is_valid(), False)

    def test_pass_with_permission(self):
        assign_perm("reply", self.user, self.letter.case.monitoring)
        data = {"body": "Lorem", "title": "Lorem", "send": "yes"}
        form = ReplyForm(user=self.user, letter=self.letter, data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_saving_not_sending(self):
        assign_perm("add_draft", self.user, self.letter.case.monitoring)
        default = {"body": "Lorem", "title": "Lorem"}
        form = ReplyForm(
            data=dict_merge(default, {"save": "yes"}),
            user=self.user,
            letter=self.letter,
        )
        self.assertTrue(form.is_valid(), msg=form.errors)
        form.save()
        self.assertEqual(len(mail.outbox), 0)
