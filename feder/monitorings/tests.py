from unittest import skip
from unittest.mock import Mock, patch

from django.core import mail
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm, get_user_perms

from feder.cases.factories import CaseFactory
from feder.cases.models import Case
from feder.cases_tags.factories import TagFactory
from feder.domains.factories import DomainFactory
from feder.institutions.factories import InstitutionFactory
from feder.letters.factories import (
    DraftLetterFactory,
    IncomingLetterFactory,
    OutgoingLetterFactory,
)
from feder.letters.models import Letter, MassMessageDraft
from feder.main.tests import PermissionStatusMixin
from feder.monitorings.filters import MonitoringFilter
from feder.parcels.factories import IncomingParcelPostFactory, OutgoingParcelPostFactory
from feder.records.factories import RecordFactory
from feder.teryt.factories import JSTFactory
from feder.users.factories import UserFactory

from .factories import MonitoringFactory
from .forms import MassMessageForm, MonitoringForm
from .models import Monitoring
from .serializers import MultiCaseTagSerializer
from .tasks import handle_mass_assign, send_letter_for_mass_assign

EXAMPLE_DATA = {
    "name": "foo-bar-monitoring",
    "description": "xyz",
    "notify_alert": True,
    "subject": "example subject",
    "template": "xyz {{EMAIL}}",
    "email_footer": "X",
}


class MonitoringFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(username="john")

    def test_form_save_user(self):
        data = {
            **EXAMPLE_DATA.copy(),
            "domain": DomainFactory().pk,
        }
        form = MonitoringForm(data, user=self.user)
        self.assertTrue(form.is_valid(), msg=form.errors)
        obj = form.save()
        self.assertEqual(obj.user, self.user)

    def test_form_template_validator(self):
        data = {**EXAMPLE_DATA.copy(), "template": "xyzyyz"}
        form = MonitoringForm(data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("template", form.errors)


class MonitoringFilterTestCase(TestCase):
    @skip("Need to discovery way to mock QuerySet")
    def test_respect_disabling_fields(self):
        mock_qs = Mock()
        voivodeship = JSTFactory(category__level=1)
        county = JSTFactory(parent=voivodeship, category__level=2)

        filter = MonitoringFilter(
            data={"voivodeship": voivodeship.pk, "county": county.pk}, queryset=mock_qs
        )

        _ = filter.qs  # Fire mock
        # [call.area(<JednostkaAdministracyjna: jst-0>)]
        self.assertEqual(len(mock_qs.all().mock_calls), 1, mock_qs.all().mock_calls)


class ObjectMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory(username="john")
        self.monitoring = self.permission_object = MonitoringFactory(subject="Wniosek")


class MonitoringCreateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    url = reverse("monitorings:create")
    permission = ["monitorings.add_monitoring"]

    def get_permission_object(self):
        return None

    def test_template_used(self):
        assign_perm("monitorings.add_monitoring", self.user)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")

    def test_assign_perm_for_creator(self):
        assign_perm("monitorings.add_monitoring", self.user)
        self.login_permitted_user()
        data = {
            **EXAMPLE_DATA.copy(),
            "domain": DomainFactory().pk,
        }
        response = self.client.post(self.get_url(), data=data)
        self.assertEqual(response.status_code, 302)
        monitoring = Monitoring.objects.get(name="foo-bar-monitoring")
        self.assertTrue(self.user.has_perm("monitorings.reply", monitoring))


class MonitoringListViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse("monitorings:list")

    def test_list_display(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_list_hide_unpublic_for_public(self):
        Monitoring.objects.filter(pk=self.monitoring.pk).update(is_public=False)
        response = self.client.get(self.get_url())

        self.assertNotContains(response, self.monitoring)

    def test_list_display_unpublic_for_member(self):
        Monitoring.objects.filter(pk=self.monitoring.pk).update(is_public=False)
        self.grant_permission("monitorings.view_quarantined_case")
        self.login_permitted_user()

        response = self.client.get(self.get_url())

        self.assertContains(response, self.monitoring)

    def test_filter_by_voivodship(self):
        # creates a new monitoring (and institution, JST, too)
        self.case = CaseFactory()

        response = self.client.get(
            reverse("monitorings:list") + f"?voivodeship={self.case.institution.jst.id}"
        )
        self.assertContains(response, self.case.monitoring)
        self.assertNotContains(response, self.monitoring)


class MonitoringReportTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.view_report"]

    def get_url(self):
        return reverse("monitorings:report", kwargs={"slug": self.monitoring.slug})

    def test_template_used(self):
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_report.html")


class IncomingParcelFactory:
    pass


class MonitoringDetailViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return self.monitoring.get_absolute_url()

    def test_details_display(self):
        response = self.client.get(self.get_url())
        self.assertContains(response, self.monitoring)

    def test_display_case(self):
        case = CaseFactory(monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertContains(response, case)

    def test_display_letter(self):
        letter = OutgoingLetterFactory(record__case__monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertContains(response, letter)

    def test_display_parcel(self):
        ipp = IncomingParcelPostFactory(record__case__monitoring=self.monitoring)
        opp = OutgoingParcelPostFactory(record__case__monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertContains(response, ipp)
        self.assertContains(response, opp)

    def test_display_invalid_record(self):
        # see following issues regarding details of source of inconsistency:
        # https://github.com/watchdogpolska/feder/issues/748
        # https://github.com/watchdogpolska/feder/issues/769
        RecordFactory(case__monitoring=self.monitoring)

    def test_skip_link_to_tag_index_if_no_permission(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse("cases_tags:list", kwargs={"monitoring": self.monitoring.pk}),
        )

    def test_show_link_to_tag_index_if_permitted(self):
        assign_perm("monitorings.view_tag", self.user, self.monitoring)
        # TODO: analyze why 'change_monitoring' is always required
        assign_perm("monitorings.change_monitoring", self.user, self.monitoring)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("cases_tags:list", kwargs={"monitoring": self.monitoring.pk}),
        )


class LetterListMonitoringViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse("monitorings:letters", kwargs={"slug": self.monitoring.slug})

    def test_list_display(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_display_letter(self):
        letter = IncomingLetterFactory(record__case__monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertContains(response, letter.body)
        self.assertContains(response, letter.note)


class DraftListMonitoringViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse("monitorings:drafts", kwargs={"slug": self.monitoring.slug})

    def test_list_display(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monitoring)

    def test_hide_draft(self):
        outgoing_letter = OutgoingLetterFactory(
            record__case__monitoring=self.monitoring
        )
        incoming_letter = IncomingLetterFactory(
            record__case__monitoring=self.monitoring
        )
        draft_letter = DraftLetterFactory(record__case__monitoring=self.monitoring)
        response = self.client.get(self.get_url())
        self.assertNotContains(
            response,
            outgoing_letter.body,
            msg_prefix="Response contains outgoing letter. ",
        )
        self.assertNotContains(
            response,
            incoming_letter.body,
            msg_prefix="Response contains incoming letter. ",
        )

        self.assertContains(response, draft_letter.body)
        self.assertContains(response, draft_letter.note)


class MonitoringUpdateViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_monitoring"]

    def get_url(self):
        return reverse("monitorings:update", kwargs={"slug": self.monitoring.slug})

    def test_template_used(self):
        assign_perm("monitorings.change_monitoring", self.user, self.monitoring)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")


class MonitoringDeleteViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.delete_monitoring"]

    def get_url(self):
        return reverse("monitorings:delete", kwargs={"slug": self.monitoring.slug})

    def test_template_used(self):
        assign_perm("monitorings.delete_monitoring", self.user, self.monitoring)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_confirm_delete.html")


class PermissionWizardTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.manage_perm"]

    def get_url(self):
        return reverse("monitorings:perm-add", kwargs={"slug": self.monitoring.slug})

    def test_template_used(self):
        assign_perm("monitorings.manage_perm", self.user, self.monitoring)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/permission_wizard.html")

    def test_set_permissions(self):
        normal_user = UserFactory(username="barney")

        assign_perm("monitorings.manage_perm", self.user, self.monitoring)
        self.login_permitted_user()

        # First step - selecting user to set permissions to
        data = {"0-user": normal_user.pk, "permission_wizard-current_step": "0"}
        response = self.client.post(self.get_url(), data=data)
        self.assertEqual(response.status_code, 200)

        # Second step - updating user's permissions
        granted_permission = ["add_case", "add_draft", "add_letter"]
        data = {
            "1-permissions": granted_permission,
            "permission_wizard-current_step": "1",
        }
        response = self.client.post(self.get_url(), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertCountEqual(
            get_user_perms(normal_user, self.monitoring), granted_permission
        )


class MonitoringPermissionViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.manage_perm"]

    def get_url(self):
        return reverse("monitorings:perm", kwargs={"slug": self.monitoring.slug})

    def test_template_used(self):
        assign_perm("monitorings.manage_perm", self.user, self.monitoring)
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_permissions.html")


class MonitoringUpdatePermissionViewTestCase(
    ObjectMixin, PermissionStatusMixin, TestCase
):
    permission = ["monitorings.manage_perm"]

    def get_url(self):
        return reverse(
            "monitorings:perm-update",
            kwargs={"slug": self.monitoring.slug, "user_pk": self.user.pk},
        )

    def test_template_used(self):
        self.grant_permission()
        self.login_permitted_user()
        response = self.client.get(self.get_url())
        self.assertTemplateUsed(response, "monitorings/monitoring_form.html")


class MonitoringAssignViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_monitoring"]

    def get_url(self):
        return reverse("monitorings:assign", kwargs={"slug": self.monitoring.slug})

    def send_all_pending(self):
        ids = list(
            {
                x
                for x in Case.objects.annotate(count=Count("record"))
                .filter(count=0)
                .all()
                .values_list("mass_assign", flat=True)
            }
        )
        for mass_assign in ids:
            handle_mass_assign.now(str(mass_assign))
        for mass_assign in ids:
            send_letter_for_mass_assign.now(str(mass_assign))

    def test_assign_display_institutions(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory(name="Office 1")
        institution_2 = InstitutionFactory(name="Office 2")
        response = self.client.get(self.get_url() + "?name=Office")
        self.assertContains(response, institution_1.name)
        self.assertContains(response, institution_2.name)

    def test_assign_display_no_institutions_whithout_filter(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory(name="Office 1")
        institution_2 = InstitutionFactory(name="Office 2")
        response = self.client.get(self.get_url())
        self.assertNotContains(response, institution_1.name)
        self.assertNotContains(response, institution_2.name)

    def test_send_to_all(self):
        self.login_permitted_user()
        InstitutionFactory(name="Office 1")
        InstitutionFactory(name="Office 2")
        InstitutionFactory()
        self.client.post(self.get_url() + "?name=Office", data={"all": "yes"})
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 2)

    def test_force_filtering_before_assign(self):
        self.login_permitted_user()
        InstitutionFactory(name="Office 1")
        InstitutionFactory(name="Office 2")
        InstitutionFactory()
        response = self.client.post(self.get_url(), data={"all": "yes"})
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 0)
        self.assertRedirects(response, self.get_url())

    def test_send_to_selected(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory(name="Office 1")
        institution_2 = InstitutionFactory(name="Office 2")
        InstitutionFactory()
        to_send_ids = [institution_1.pk, institution_2.pk]
        self.client.post(
            self.get_url() + "?name=Office", data={"to_assign": to_send_ids}
        )
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], institution_1.email)
        self.assertEqual(mail.outbox[1].to[0], institution_2.email)
        for x in (0, 1):
            self.assertEqual(mail.outbox[x].subject, "Wniosek")

    def test_update_email_after_send(self):
        self.login_permitted_user()
        institution = InstitutionFactory(name="Office 1")
        to_send_ids = [institution.pk]
        self.client.post(
            self.get_url() + "?name=Office", data={"to_assign": to_send_ids}
        )
        self.send_all_pending()
        case = Case.objects.filter(
            monitoring=self.monitoring, institution=institution
        ).get()
        self.assertTrue(case.email)

    def test_constant_increment_local_id(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory(name="Office 1")
        institution_2 = InstitutionFactory(name="Office 2")
        institution_3 = InstitutionFactory(name="Office 3")
        self.client.post(
            self.get_url() + "?name=Office", data={"to_assign": [institution_1.pk]}
        )
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 1)

        self.assertTrue(
            Case.objects.latest().name.endswith(" #1"), msg=Case.objects.latest().name
        )

        self.client.post(
            self.get_url() + "?name=Office",
            data={"to_assign": [institution_2.pk, institution_3.pk]},
        )
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 3)
        self.assertTrue(institution_2.case_set.all()[0].name.endswith(" #2"))
        self.assertTrue(institution_3.case_set.all()[0].name.endswith(" #3"))

        for x in (0, 1, 2):
            self.assertEqual(mail.outbox[x].subject, "Wniosek")

    def test_hide_new_cases_propagation(self):
        self.login_permitted_user()
        institution_1 = InstitutionFactory(name="Office 1")
        self.client.post(
            self.get_url() + "?name=Office", data={"to_assign": [institution_1.pk]}
        )
        self.send_all_pending()
        self.assertFalse(institution_1.case_set.all()[0].is_quarantined)

        self.monitoring.hide_new_cases = True
        self.monitoring.save()
        institution_2 = InstitutionFactory(name="Office 2")
        self.client.post(
            self.get_url() + "?name=Office", data={"to_assign": [institution_2.pk]}
        )
        self.send_all_pending()
        self.assertTrue(institution_2.case_set.all()[0].is_quarantined)

    @patch(
        "feder.monitorings.views.MonitoringAssignView.get_limit_simultaneously",
        Mock(return_value=10),
    )
    def test_limit_number_of_letters_sent_simultaneously(self):
        self.login_permitted_user()
        InstitutionFactory.create_batch(size=25, name="Office")

        response = self.client.post(
            self.get_url() + "?name=Office", data={"all": "yes"}
        )
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 0)
        self.assertRedirects(response, self.get_url())

    def test_assing_using_custom_domain(self):
        self.monitoring.domain = DomainFactory(name="custom-domain.com")
        self.monitoring.save()
        self.login_permitted_user()
        InstitutionFactory(name="Office 1")
        InstitutionFactory(name="Office 2")
        InstitutionFactory()
        self.client.post(self.get_url() + "?name=Office", data={"all": "yes"})
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 2)

    def test_assign_using_organisation(self):
        self.monitoring.domain = DomainFactory(organisation__name="angel-corp")
        self.monitoring.save()
        self.login_permitted_user()
        InstitutionFactory(name="Office 1")
        self.client.post(self.get_url() + "?name=Office", data={"all": "yes"})
        self.send_all_pending()
        self.assertEqual(len(mail.outbox), 1)
        # reply to email should have organisation name
        self.assertTrue("angel-corp" in mail.outbox[0].from_email)


class SitemapTestCase(ObjectMixin, TestCase):
    def test_monitorings(self):
        url = reverse("sitemaps", kwargs={"section": "monitorings"})
        needle = reverse("monitorings:details", kwargs={"slug": self.monitoring.slug})
        response = self.client.get(url)
        self.assertContains(response, needle)

    def test_monitorings_pages(self):
        url = reverse("sitemaps", kwargs={"section": "monitorings_pages"})
        needle = reverse(
            "monitorings:details", kwargs={"slug": self.monitoring.slug, "page": 1}
        )
        response = self.client.get(url)
        self.assertContains(response, needle)


class MultiCaseTagManagementTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.change_case"]
    status_anonymous = 401
    status_no_permission = 403
    status_has_permission = 202

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(monitoring=self.monitoring)
        self.tag_global = TagFactory(name="global", monitoring=None)
        self.tag_local = TagFactory(name="local", monitoring=self.monitoring)

    def get_url(self):
        return reverse(
            "monitoring-case-tags-update", kwargs={"monitoring_pk": self.monitoring.pk}
        )

    def get_form_data(self, case_ids=None, tag_ids=None, operation=None):
        return {
            "cases": case_ids or [self.case.id],
            "tags": tag_ids or [],
            "operation": operation or MultiCaseTagSerializer.OPERATIONS.add,
        }

    def test_status_code_for_privileged_user(self):
        self.grant_permission()
        self.client.login(username="john", password="pass")
        response = self.client.post(self.get_url(), data=self.get_form_data())
        self.assertEqual(response.status_code, self.status_has_permission)

    def test_add_tags(self):
        # no case tags yet
        self.assertEqual(self.case.tags.all().count(), 0)

        # posting to API to add tags
        self.grant_permission()
        self.client.login(username="john", password="pass")
        response = self.client.post(
            self.get_url(),
            data=self.get_form_data(
                tag_ids=[self.tag_global.id, self.tag_local.id],
                operation=MultiCaseTagSerializer.OPERATIONS.add,
            ),
        )
        self.assertEqual(response.status_code, 202)

        # both tags should now be assigned with the case
        case_tags = self.case.tags.all()
        self.assertIn(self.tag_global, case_tags)
        self.assertIn(self.tag_local, case_tags)

    def test_remove_tags(self):
        self.case.tags.add(self.tag_local)
        self.case.tags.add(self.tag_global)

        # both tags assigned
        case_tags = self.case.tags.all()
        self.assertIn(self.tag_global, case_tags)
        self.assertIn(self.tag_local, case_tags)

        # posting to API to remove the tags
        self.grant_permission()
        self.client.login(username="john", password="pass")
        response = self.client.post(
            self.get_url(),
            data=self.get_form_data(
                tag_ids=[self.tag_global.id, self.tag_local.id],
                operation=MultiCaseTagSerializer.OPERATIONS.remove,
            ),
        )
        self.assertEqual(response.status_code, 202)

        # case should have no tags assigned
        self.assertEqual(self.case.tags.all().count(), 0)


class MassMessageViewTestCase(ObjectMixin, PermissionStatusMixin, TestCase):
    permission = ["monitorings.add_draft"]
    status_anonymous = 302  # redirects to login page
    status_no_permission = 403
    status_has_permission = 200

    def setUp(self):
        super().setUp()
        self.case1_tag = TagFactory(monitoring=self.monitoring, name="case1_tag")
        self.case2_tag = TagFactory(monitoring=self.monitoring, name="case2_tag")
        self.global_tag = TagFactory(monitoring=None, name="global_tag")
        self.not_used_tag = TagFactory(monitoring=self.monitoring, name="not_used_tag")
        self.case1 = CaseFactory(monitoring=self.monitoring, tags=[self.case1_tag])
        self.case2 = CaseFactory(monitoring=self.monitoring, tags=[self.case2_tag])
        self.case3 = CaseFactory(monitoring=self.monitoring, tags=[self.global_tag])
        self.case4 = CaseFactory(monitoring=self.monitoring)

    def get_url(self):
        return reverse(
            "monitorings:mass-message", kwargs={"slug": self.monitoring.slug}
        )

    def get_form_data(self, **kwargs):
        data = {}
        form = MassMessageForm(self.monitoring, user=self.user)
        for field_name in [
            "recipients_tags",
            "title",
            "html_body",
            "html_quote",
            "note",
        ]:
            data[field_name] = kwargs.get(field_name) or form.fields[field_name]
        if "send" in kwargs.keys():
            data["send"] = "send"
        data.update(
            **{
                "attachment_set-TOTAL_FORMS": 0,
                "attachment_set-INITIAL_FORMS": 0,
                "attachment_set-MAX_NUM_FORMS": 1,
            }
        )
        return data

    def check_template_used(self):
        self.grant_permission()
        self.client.login(username="john", password="pass")
        response = self.client.get()
        self.assertTemplateUsed(response, "monitorings/mass_message.html")

    def test_create_mass_draft(self):
        # Ensuring no Letter objects yet
        self.assertEqual(Letter.objects.all().count(), 0)

        # posting to API to create mass draft
        self.grant_permission()
        self.client.login(username="john", password="pass")
        response = self.client.post(
            self.get_url(),
            data=self.get_form_data(
                recipients_tags=[
                    self.case1_tag.pk,
                    self.case2_tag.pk,
                    self.global_tag.pk,
                ]
            ),
        )
        self.assertEqual(response.status_code, 302)  # redirection after success

        # getting mass draft letter object
        mass_draft = Letter.objects.get(message_type=Letter.MESSAGE_TYPES.mass_draft)
        self.assertTrue(mass_draft.is_mass_draft())
        self.assertEqual(
            response.url, reverse("letters:details", kwargs={"pk": mass_draft.pk})
        )

        # ensuring no regular letters has been created
        self.assertFalse(
            Letter.objects.exclude(
                message_type=Letter.MESSAGE_TYPES.mass_draft
            ).exists()
        )

    def test_create_mass_message(self):
        # Ensuring no Letter objects yet
        self.assertEqual(Letter.objects.all().count(), 0)

        # grant additional permission for sending message
        self.grant_permission("monitorings.reply")

        # posting to API to send mass message
        self.client.login(username="john", password="pass")
        response = self.client.post(
            self.get_url(),
            data=self.get_form_data(
                recipients_tags=[
                    self.case1_tag.pk,
                    self.case2_tag.pk,
                    self.global_tag.pk,
                ],
                send="send",
            ),
        )

        self.assertEqual(response.status_code, 302)  # redirection after success
        self.assertEqual(
            response.url,
            reverse("monitorings:details", kwargs={"slug": self.monitoring.slug}),
        )

        # letters will be sent asynchronously, so we only can check draft here
        draft = MassMessageDraft.objects.get()
        recipients_tags = draft.recipients_tags.all()
        self.assertIn(self.case1_tag, recipients_tags)
        self.assertIn(self.case2_tag, recipients_tags)
        self.assertIn(self.global_tag, recipients_tags)


class MonitoringFeedTestCaseMixin:
    def test_simple_render(self):
        resp = self.client.get(self.get_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.monitoring.name)


class MonitoringRssFeedTestCase(
    MonitoringFeedTestCaseMixin, ObjectMixin, PermissionStatusMixin, TestCase
):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse("monitorings:rss")


class MonitoringAtomFeedTestCase(
    MonitoringFeedTestCaseMixin, ObjectMixin, PermissionStatusMixin, TestCase
):
    status_anonymous = 200
    status_no_permission = 200
    permission = []

    def get_url(self):
        return reverse("monitorings:atom")
