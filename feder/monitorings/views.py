from datetime import datetime

from ajax_datatable import AjaxDatatableView
from atom.views import DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    LoginRequiredMixin,
    MessageMixin,
    PermissionRequiredMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from cached_property import cached_property
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.feedgenerator import Atom1Feed
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView
from extra_views import CreateWithInlinesView
from formtools.wizard.views import SessionWizardView
from guardian.shortcuts import assign_perm
from guardian.utils import get_anonymous_user
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from feder.cases.models import Case
from feder.cases_tags.models import Tag
from feder.institutions.filters import InstitutionFilter
from feder.institutions.models import Institution
from feder.letters.formsets import AttachmentInline
from feder.letters.models import Letter
from feder.letters.utils import is_formatted_html
from feder.letters.views import LetterCommonMixin
from feder.main.mixins import ExtraListMixin, RaisePermissionRequiredMixin
from feder.main.paginator import DefaultPagination
from feder.teryt.models import JST

from .filters import (
    MonitoringCaseAreaFilter,
    MonitoringCaseReportFilter,
    MonitoringFilter,
)
from .forms import (
    CheckboxTranslatedUserObjectPermissionsForm,
    MassMessageForm,
    MonitoringForm,
    SaveTranslatedUserObjectPermissionsForm,
    SelectUserForm,
)
from .models import Monitoring
from .permissions import MultiCaseTagManagementPerm
from .serializers import MultiCaseTagSerializer
from .tasks import handle_mass_assign, send_mass_draft


class MonitoringListView(SelectRelatedMixin, FilterView):
    filterset_class = MonitoringFilter
    model = Monitoring
    select_related = ["user"]
    paginate_by = 25

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .for_user(self.request.user)
            .with_case_count()
            .order_by("-created")
        )


class MonitoringsTableView(TemplateView):
    """
    View for displaying template with Monitorings table.
    """

    template_name = "monitorings/monitorings_table.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header_label"] = mark_safe(_("Monitorings search table"))
        context["ajax_datatable_url"] = reverse(
            "monitorings:monitorings_table_ajax_data"
        )
        return context


class MonitoringsAjaxDatatableView(AjaxDatatableView):
    """
    View to provide table list of all Monitorings with ajax data.
    """

    model = Monitoring
    title = _("Monitorings")
    initial_order = [
        ["id", "desc"],
    ]
    length_menu = [[200, 20, 50, 100], [200, 20, 50, 100]]
    search_values_separator = "|"
    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {"name": "id", "visible": True, "title": "Id"},
        {
            "name": "created_str",
            "visible": True,
            "width": 130,
            # "max_length": 16,
            "title": _("Created"),
        },
        {
            "name": "name",
            "visible": True,
            "width": 300,
            "title": _("Name"),
        },
        {
            "name": "description",
            "visible": True,
            "width": 300,
            "title": _("Description"),
        },
        {
            "name": "user",
            "visible": True,
            "title": _("User"),
            "foreign_field": "user__username",
        },
        {
            "name": "case_count",
            "visible": True,
            "searchable": False,
            "title": _("Case count"),
        },
        {
            "name": "case_quarantined_count",
            "visible": True,
            "searchable": False,
            "title": _("Case quarantined count"),
        },
        {
            "name": "case_confirmation_received_count",
            "visible": True,
            "searchable": False,
            "title": _("Confirmation received count"),
        },
        {
            "name": "case_response_received_count",
            "visible": True,
            "searchable": False,
            "title": _("Response received count"),
        },
        {
            "name": "hide_new_cases",
            "visible": True,
            "title": _("Hide new cases when assigning?"),
            "searchable": False,
        },
        {
            "name": "is_public",
            "visible": True,
            "title": _("Is public visible?"),
            "searchable": False,
        },
        {
            "name": "notify_alert",
            "visible": True,
            "title": _("Notify about alerts"),
            "searchable": False,
        },
    ]

    def get_initial_queryset(self, request=None):
        qs = super().get_initial_queryset(request).prefetch_related()
        return (
            qs.for_user(user=self.request.user)
            .with_formatted_datetime("created", timezone.get_default_timezone())
            .with_case_count()
            .with_case_confirmation_received_count()
            .with_case_response_received_count()
            .with_case_quarantined_count()
        )

    def render_row_details(self, pk, request=None):
        obj = self.model.objects.filter(id=pk).first()
        fields_to_skip = [
            "slug",
        ]
        fields = [
            f.name
            for f in obj._meta.get_fields()
            if f.concrete and f.name not in fields_to_skip
        ]
        html = '<table class="table table-bordered compact" style="max-width: 70%;">'
        for field in fields:
            try:
                value = getattr(obj, field) or ""
                if field in ["template", "email_footer", "description"]:
                    value = (
                        mark_safe(value)
                        if is_formatted_html(value)
                        else mark_safe(linebreaksbr(value.replace("\r", "")))
                    )
                elif isinstance(value, datetime):
                    value = timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S")
                elif field in ["hide_new_cases", "is_public", "notify_alert"]:
                    value = _("Yes") if value else _("No")
                verbose_n = obj._meta.get_field(field).verbose_name
            except AttributeError:
                continue
            html += f'<tr><td style="width: 20%;">{verbose_n}</td><td>{value}</td></tr>'
        html += "</table>"
        return mark_safe(html)

    def customize_row(self, row, obj):
        row["name"] = obj.render_monitoring_cases_table_link()
        row["hide_new_cases"] = obj.render_boolean_field("hide_new_cases")
        row["is_public"] = obj.render_boolean_field("is_public")
        row["notify_alert"] = obj.render_boolean_field("notify_alert")


class MonitoringCasesTableView(FilterView):
    """
    View for displaying template with table of Monitoring Cases.
    """

    model = Monitoring
    filterset_class = MonitoringCaseAreaFilter
    template_name = "monitorings/monitoring_cases_table.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        monitoring = Monitoring.objects.get(slug=self.kwargs.get("slug"))
        context["header_label"] = mark_safe(
            _("Monitoring Cases table - ") + monitoring.name
        )
        context["ajax_datatable_url"] = reverse(
            "monitorings:monitoring_cases_table_ajax_data",
            kwargs={"slug": self.kwargs.get("slug")},
        )
        context["datatable_id"] = "monitoring_cases_table"
        context["area_filter_form"] = MonitoringCaseAreaFilter().form
        return context


class MonitoringCasesAjaxDatatableView(AjaxDatatableView):
    """
    View to provide table list of all Monitoring Cases with ajax data.
    """

    model = Case
    title = _("Monitoring Cases")
    initial_order = [
        ["id", "desc"],
    ]
    length_menu = [[20, 50, 100], [20, 50, 100]]
    search_values_separator = "|"
    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {"name": "id", "visible": True, "title": "Id"},
        # {
        #     "name": "created_str",
        #     "visible": True,
        #     "width": 130,
        #     # "max_length": 16,
        #     "title": _("Created"),
        # },
        {
            "name": "name",
            "visible": True,
            # "width": 600,
            "title": _("Name"),
        },
        {
            "name": "institution",
            "visible": True,
            "title": _("Institution"),
        },
        {
            "name": "institution_jst",
            "visible": True,
            "title": _("JST"),
            "foreign_field": "institution__jst",
            "searchable": False,
        },
        {
            "name": "record_max_str",
            "visible": True,
            "title": _("Last letter"),
        },
        {
            "name": "record_max",
            "visible": False,
        },
        {
            "name": "record_count",
            "visible": True,
            "title": _("Letters count"),
            "searchable": False,
        },
        {
            "name": "tags",
            "visible": True,
            "title": _("Tags"),
            "choices": True,
            "autofilter": True,
            "m2m_foreign_field": "tags__name",
        },
        {
            "name": "confirmation_received",
            "visible": True,
            "title": _("Conf."),
            "searchable": False,
        },
        {
            "name": "response_received",
            "visible": True,
            "title": _("Resp."),
            "searchable": False,
        },
        {
            "name": "is_quarantined",
            "visible": True,
            "title": _("Quar."),
            "searchable": False,
        },
    ]

    def get_initial_queryset(self, request=None):
        slug = self.kwargs.get("slug")
        monitoring = Monitoring.objects.get(slug=slug)
        qs = (
            super()
            .get_initial_queryset(request)
            .filter(monitoring=monitoring)
            .select_related(
                "institution",
                "institution__jst",
            )
            .prefetch_related()
        )
        qs = qs.ajax_boolean_filter(self.request, "conf_", "confirmation_received")
        qs = qs.ajax_boolean_filter(self.request, "resp_", "response_received")
        qs = qs.ajax_boolean_filter(self.request, "quar_", "is_quarantined")
        qs = qs.ajax_area_filter(self.request)
        return (
            qs.for_user(user=self.request.user)
            # .with_formatted_datetime("created", timezone.get_default_timezone())
            .with_record_max()
            .with_record_max_str()
            .with_record_count()
        )

    def customize_row(self, row, obj):
        row["confirmation_received"] = obj.render_boolean_field("confirmation_received")
        row["response_received"] = obj.render_boolean_field("response_received")
        row["is_quarantined"] = obj.render_boolean_field("is_quarantined")
        row["name"] = obj.render_case_link()
        row["institution_jst"] = obj.institution.jst.tree_name

    def get_latest_by(self, request):
        return "record_max"


class MonitoringDetailView(SelectRelatedMixin, ExtraListMixin, DetailView):
    model = Monitoring
    select_related = ["user"]
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.for_user(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        kwargs["url_extra_kwargs"] = {"slug": self.object.slug}
        context = super().get_context_data(**kwargs)
        context["voivodeship_table"] = self.generate_voivodeship_table(self.object)
        return context

    def get_object_list(self, obj):
        return (
            Case.objects.filter(monitoring=obj)
            .select_related("institution")
            .with_record_max()
            .with_letter()
            .for_user(self.request.user)
            .order_by("-record_max")
            .all()
        )

    def generate_voivodeship_table(self, monitoring):
        """
        Generate html table with monitoring voivodeships and their
        institutions and cases counts
        """
        voivodeship_list = JST.objects.filter(category__level=1).all().order_by("name")
        table = """
            <table class="table table-bordered compact" style="width: 100%">
            """
        table += """
            <tr>
                <th>Województwo</th>
                <th>Liczba spraw</th>
                <th>Liczba spraw w kwarantannie</th>
            </tr>"""
        for voivodeship in voivodeship_list:
            table += (
                "<tr><td>"
                + voivodeship.name
                + "</td><td>"
                + str(
                    Case.objects.filter(monitoring=monitoring).area(voivodeship).count()
                )
                + "</td><td>"
                + str(
                    Case.objects.filter(monitoring=monitoring, is_quarantined=True)
                    .area(voivodeship)
                    .count()
                )
                + "</td></tr>"
            )
        table += "</table>"
        return table


class LetterListMonitoringView(SelectRelatedMixin, ExtraListMixin, DetailView):
    model = Monitoring
    template_name_suffix = "_letter_list"
    select_related = ["user"]
    paginate_by = 25

    def get_context_data(self, **kwargs):
        kwargs["url_extra_kwargs"] = {"slug": self.object.slug}
        return super().get_context_data(**kwargs)

    def get_object_list(self, obj):
        return (
            Letter.objects.filter(record__case__monitoring=obj)
            .select_related("record__case")
            .with_author()
            .attachment_count()
            .exclude_spam()
            .for_user(self.request.user)
            .order_by("-created")
            .all()
        )


class MonitoringReportView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    model = Case
    filterset_class = MonitoringCaseReportFilter
    paginate_by = 100
    permission_required = "monitorings.view_report"
    object_level_permissions = True
    raise_exception = True
    redirect_unauthenticated_users = True

    def get_template_names(self):
        return "monitorings/monitoring_report.html"

    def get_object(self):
        return Monitoring.objects.get(slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring"] = self.get_object()
        context["tags"] = Tag.objects.for_monitoring(context["monitoring"])
        get_params = {key: value for key, value in context["filter"].data.items()}
        get_params["format"] = "csv"
        get_params["page_size"] = DefaultPagination.max_page_size
        get_params["monitoring"] = context["monitoring"].id
        context["csv_url"] = "{}?{}".format(
            reverse_lazy("case-report-list"), urlencode(get_params)
        )
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(monitoring__slug=self.kwargs["slug"])
            .with_institution()
            .with_application_letter_date()
            .with_application_letter_status()
            .order_by(
                "institution__jst__parent__parent__name",
                "institution__jst__parent__name",
                "institution__jst__name",
                "institution__name",
            )
        )


class DraftListMonitoringView(SelectRelatedMixin, ExtraListMixin, DetailView):
    model = Monitoring
    template_name_suffix = "_draft_list"
    select_related = ["user"]
    paginate_by = 25

    def get_context_data(self, **kwargs):
        kwargs["url_extra_kwargs"] = {"slug": self.object.slug}
        return super().get_context_data(**kwargs)

    def get_object_list(self, obj):
        return (
            Letter.objects.filter(
                Q(record__case__monitoring=obj) | Q(mass_draft__monitoring=obj)
            )
            .is_draft()
            .select_related("record__case")
            .with_author()
            .exclude_spam()
            .for_user(self.request.user)
            .attachment_count()
            .order_by("-created")
            .all()
        )


class MonitoringCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, UserFormKwargsMixin, CreateView
):
    model = Monitoring
    template_name = "monitorings/monitoring_form.html"
    form_class = MonitoringForm
    permission_required = "monitorings.add_monitoring"
    raise_exception = True
    redirect_unauthenticated_users = True

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)

    def form_valid(self, form):
        output = super().form_valid(form)
        default_perm = [
            "change_monitoring",
            "delete_monitoring",
            "add_case",
            "change_case",
            "delete_case",
            "reply",
            "view_alert",
            "change_alert",
            "delete_alert",
            "manage_perm",
            "add_draft",
        ]
        for perm in default_perm:
            assign_perm(perm, self.request.user, form.instance)
        return output


class MonitoringUpdateView(
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    UpdateMessageMixin,
    FormValidMessageMixin,
    UpdateView,
):
    model = Monitoring
    form_class = MonitoringForm
    permission_required = "monitorings.change_monitoring"


class MonitoringDeleteView(
    RaisePermissionRequiredMixin, DeleteMessageMixin, DeleteView
):
    model = Monitoring
    success_url = reverse_lazy("monitorings:list")
    permission_required = "monitorings.delete_monitoring"


class PermissionWizard(LoginRequiredMixin, SessionWizardView):
    form_list = [SelectUserForm, CheckboxTranslatedUserObjectPermissionsForm]
    template_name = "monitorings/permission_wizard.html"

    def perm_check(self):
        if not self.request.user.has_perm("monitorings.manage_perm", self.monitoring):
            raise PermissionDenied()

    @cached_property
    def monitoring(self):
        return Monitoring.objects.get(slug=self.kwargs["slug"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["object"] = self.monitoring
        return context

    def get_form_kwargs(self, step=None):
        kw = super().get_form_kwargs(step)
        self.perm_check()
        if step == "1":
            user_pk = self.storage.get_step_data("0").get("0-user")
            user = get_user_model().objects.get(pk=user_pk)
            kw["user"] = user
            kw["obj"] = self.monitoring
        return kw

    def get_success_message(self):
        return _("Permissions to {monitoring} updated!").format(monitoring=self.object)

    def done(self, form_list, form_dict, *args, **kwargs):
        form = form_dict["1"]
        form.save_obj_perms()
        self.object = form.obj
        messages.success(self.request, self.get_success_message())
        url = reverse("monitorings:perm", kwargs={"slug": self.object.slug})
        return HttpResponseRedirect(url)


class MonitoringPermissionView(
    RaisePermissionRequiredMixin, SelectRelatedMixin, DetailView
):
    model = Monitoring
    template_name_suffix = "_permissions"
    select_related = ["user"]
    permission_required = "monitorings.manage_perm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_list"], context["index"] = self.object.permission_map()
        return context


class MonitoringUpdatePermissionView(
    RaisePermissionRequiredMixin, SelectRelatedMixin, FormView
):
    form_class = SaveTranslatedUserObjectPermissionsForm
    template_name = "monitorings/monitoring_form.html"
    permission_required = "monitorings.manage_perm"

    def get_permission_object(self):
        return self.get_monitoring()

    def get_user(self):
        if not getattr(self, "user", None):
            self.user = get_object_or_404(get_user_model(), id=self.kwargs["user_pk"])
        return self.user

    def get_monitoring(self):
        if not getattr(self, "monitoring", None):
            self.monitoring = get_object_or_404(Monitoring, slug=self.kwargs["slug"])
        return self.monitoring

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_monitoring()
        return context

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update({"user": self.get_user(), "obj": self.get_monitoring()})
        return kw

    def get_success_message(self):
        return _("Permissions to {monitoring} of {user} updated!").format(
            monitoring=self.monitoring, user=self.user
        )

    def form_valid(self, form):
        form.save_obj_perms()
        messages.success(self.request, self.get_success_message())
        url = reverse("monitorings:perm", kwargs={"slug": self.get_monitoring().slug})
        return HttpResponseRedirect(url)


class MonitoringAssignView(RaisePermissionRequiredMixin, FilterView):
    model = Institution
    filterset_class = InstitutionFilter
    permission_required = "monitorings.change_monitoring"
    template_name = "monitorings/institution_assign.html"
    paginate_by = 50
    LIMIT = 500

    def get_limit_simultaneously(self):
        return self.LIMIT

    def get_queryset(self):
        qs = super().get_queryset().order_by("name")
        return (
            qs.exclude(case__monitoring=self.monitoring.pk)
            .with_case_count()
            .select_related("jst")
        )

    def get_permission_object(self):
        return self.monitoring

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring"] = self.monitoring
        context["is_filtered"] = self.is_filtered()
        return context

    def is_filtered(self):
        count = sum(1 for value in self.request.GET.values() if value)
        return bool(self.request.GET and count > 0)

    def get_filterset_kwargs(self, filterset_class):
        kw = super().get_filterset_kwargs(filterset_class)
        return kw

    def post(self, request, *args, **kwargs):
        if not self.is_filtered():
            msg = _("You can not send letters without using filtering.")
            messages.error(self.request, msg)
            return HttpResponseRedirect(self.request.path)

        if request.POST.get("all", "no") == "yes":
            qs = self.get_filterset(self.get_filterset_class()).qs
        else:
            ids = request.POST.getlist("to_assign")
            qs = Institution.objects.filter(pk__in=ids)
        qs = qs.exclude(case__monitoring=self.monitoring.pk)

        count = Case.objects.filter(monitoring=self.monitoring).count() or 0

        to_assign_count = qs.count()
        if to_assign_count > self.get_limit_simultaneously():
            msg = _(
                "You can not send %(count)d letters at once. "
                "The maximum is %(limit)d. Use filtering."
            ) % {"count": to_assign_count, "limit": self.get_limit_simultaneously()}
            messages.error(self.request, msg)
            return HttpResponseRedirect(self.request.path)
        cases = []
        mass_assign = Case.objects.get_mass_assign_uid()
        for i, institution in enumerate(qs):
            postfix = " #%d" % (i + count + 1,)
            cases.append(
                Case(
                    user=self.request.user,
                    name=self.monitoring.name + postfix,
                    monitoring=self.monitoring,
                    institution=institution,
                    mass_assign=mass_assign,
                    is_quarantined=self.monitoring.hide_new_cases,
                )
            )
        Case.objects.bulk_create(cases)
        handle_mass_assign(mass_assign.hex)
        msg = _(
            "%(count)d institutions was assigned to %(monitoring)s. "
            + " The requests scheduled to sent."
        ) % {"count": to_assign_count, "monitoring": self.monitoring}
        messages.success(self.request, msg)
        url = reverse("monitorings:assign", kwargs={"slug": self.monitoring.slug})
        return HttpResponseRedirect(url)


class MassMessageView(
    LetterCommonMixin,
    RaisePermissionRequiredMixin,
    UserFormKwargsMixin,
    MessageMixin,
    CreateWithInlinesView,
):
    template_name = "monitorings/mass_message.html"
    model = Letter
    form_class = MassMessageForm
    inlines = [AttachmentInline]
    permission_required = ["monitorings.add_draft"]

    def dispatch(self, request, *args, **kwargs):
        self.monitoring = Monitoring.objects.get(slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if "send" in self.request.POST:
            return reverse("monitorings:details", kwargs={"slug": self.kwargs["slug"]})
        else:
            return super().get_success_url()

    def get_permission_object(self):
        return self.monitoring

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["monitoring"] = self.monitoring
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring"] = self.monitoring
        return context

    def forms_valid(self, form, inlines):
        result = super().forms_valid(form, inlines)

        if "send" in self.request.POST:
            cases_count = self.object.mass_draft.determine_cases().count()
            send_mass_draft(self.object.pk)
            self.messages.success(
                _(
                    'Message "{letter}" has been scheduled for sending '
                    "to {count} recipients!"
                ).format(letter=self.object, count=cases_count),
                fail_silently=True,
            )
        else:
            self.messages.success(
                _("Message {message} saved to review!").format(message=self.object),
                fail_silently=True,
            )

        return result


class MonitoringAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Monitoring.objects
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        qs = qs.for_user(self.request.user)
        return qs.all()


class UserMonitoringAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = (
            get_user_model()
            .objects.annotate(case_count=Count("case"))
            .filter(case_count__gt=0)
            .all()
        )
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.all()


# DRF views:


class MultiCaseTagManagement(APIView):
    permission_classes = [MultiCaseTagManagementPerm]

    def get_object(self):
        try:
            obj = Monitoring.objects.get(pk=self.kwargs.get("monitoring_pk"))
        except Monitoring.DoesNotExist:
            obj = None
        return obj

    def post(self, request, monitoring_pk, format=None):
        monitoring = self.get_object()
        serializer = MultiCaseTagSerializer(monitoring=monitoring, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MonitoringRssFeed(Feed):
    title = _("Latest monitorings")
    link = reverse_lazy("monitorings:list")
    description = _("Updates on new monitorings on site")
    feed_url = reverse_lazy("monitorings:rss")

    def items(self):
        return (
            Monitoring.objects.for_user(get_anonymous_user())
            .with_feed_item()
            .order_by("-created")[:30]
        )

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_author_name(self, item):
        return force_str(item.user)

    def item_author_link(self, item):
        return item.user.get_absolute_url()

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified


class MonitoringAtomFeed(MonitoringRssFeed):
    feed_type = Atom1Feed
    subtitle = MonitoringRssFeed.description
    feed_url = reverse_lazy("monitorings:atom")
