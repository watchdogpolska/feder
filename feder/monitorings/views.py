from atom.views import DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    MessageMixin,
    FormValidMessageMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from cached_property import cached_property
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import get_user_model
from guardian.utils import get_anonymous_user
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlencode
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    UpdateView,
)
from django.contrib.syndication.views import Feed
from django.utils.encoding import force_text
from django.utils.feedgenerator import Atom1Feed
from django_filters.views import FilterView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from formtools.wizard.views import SessionWizardView
from guardian.shortcuts import assign_perm
from feder.cases.models import Case
from feder.institutions.filters import InstitutionFilter
from feder.institutions.models import Institution
from feder.letters.models import Letter
from feder.main.mixins import ExtraListMixin, RaisePermissionRequiredMixin
from feder.main.paginator import DefaultPagination
from feder.cases_tags.models import Tag
from .filters import MonitoringFilter, MonitoringCaseReportFilter
from .forms import (
    MonitoringForm,
    SaveTranslatedUserObjectPermissionsForm,
    SelectUserForm,
    CheckboxTranslatedUserObjectPermissionsForm,
    MassMessageForm,
)
from .models import Monitoring
from .permissions import MultiCaseTagManagementPerm
from .serializers import MultiCaseTagSerializer
from .tasks import handle_mass_assign, send_mass_draft
from feder.letters.formsets import AttachmentInline
from feder.letters.views import LetterCommonMixin
from extra_views import CreateWithInlinesView


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
        return super().get_context_data(**kwargs)

    def get_object_list(self, obj):
        return (
            Case.objects.filter(monitoring=obj)
            .select_related("institution")
            .with_record_max()
            .with_letter()
            .order_by("-record_max")
            .all()
        )


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
        qs = super().get_queryset()
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
        return context

    def get_filterset_kwargs(self, filterset_class):
        kw = super().get_filterset_kwargs(filterset_class)
        return kw

    def post(self, request, *args, **kwargs):
        if not request.GET:
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
        return force_text(item.user)

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
