from atom.ext.guardian.forms import TranslatedUserObjectPermissionsForm
from atom.views import DeleteMessageMixin, UpdateMessageMixin
from braces.views import (FormValidMessageMixin, LoginRequiredMixin,
                          PermissionRequiredMixin, SelectRelatedMixin,
                          UserFormKwargsMixin, PrefetchRelatedMixin)
from cached_property import cached_property
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  UpdateView)
from django_filters.views import FilterView
from formtools.wizard.views import SessionWizardView
from guardian.shortcuts import assign_perm

from feder.cases.models import Case
from feder.institutions.filters import InstitutionFilter
from feder.institutions.models import Institution
from feder.letters.models import Letter
from feder.main.mixins import ExtraListMixin, RaisePermissionRequiredMixin
from .filters import MonitoringFilter
from .forms import (MonitoringForm, SaveTranslatedUserObjectPermissionsForm,
                    SelectUserForm)
from .models import Monitoring


class MonitoringListView(SelectRelatedMixin, FilterView):
    filterset_class = MonitoringFilter
    model = Monitoring
    select_related = ['user', ]
    paginate_by = 25

    def get_queryset(self):
        qs = super(MonitoringListView, self).get_queryset()
        return qs.with_case_count()


class MonitoringDetailView(SelectRelatedMixin, PrefetchRelatedMixin,
                           ExtraListMixin, DetailView):
    model = Monitoring
    select_related = ['user', ]
    prefetch_related = ['questionary_set', ]
    paginate_by = 25

    @staticmethod
    def get_object_list(obj):
        return (Case.objects.filter(monitoring=obj).
                select_related('institution').
                prefetch_related('task_set').
                with_letter_max().
                with_letter().
                order_by('-letter_max').
                all())


class MonitoringCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                           UserFormKwargsMixin, CreateView):
    model = Monitoring
    template_name = 'monitorings/monitoring_form.html'
    form_class = MonitoringForm
    permission_required = 'monitorings.add_monitoring'
    raise_exception = True
    redirect_unauthenticated_users = True

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)

    def form_valid(self, form):
        output = super(MonitoringCreateView, self).form_valid(form)
        default_perm = ['change_monitoring', 'delete_monitoring', 'add_questionary',
                        'change_questionary', 'delete_questionary', 'add_case',
                        'change_case', 'delete_case', 'add_task', 'change_task',
                        'delete_task', 'reply', 'view_alert', 'change_alert',
                        'delete_alert', 'manage_perm',
                        'select_survey', 'add_draft']
        for perm in default_perm:
            assign_perm(perm, self.request.user, form.instance)
        return output


class MonitoringUpdateView(RaisePermissionRequiredMixin, UserFormKwargsMixin,
                           UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Monitoring
    form_class = MonitoringForm
    permission_required = 'monitorings.change_monitoring'


class MonitoringDeleteView(RaisePermissionRequiredMixin, DeleteMessageMixin,
                           DeleteView):
    model = Monitoring
    success_url = reverse_lazy('monitorings:list')
    permission_required = 'monitorings.delete_monitoring'


class PermissionWizard(LoginRequiredMixin, SessionWizardView):
    form_list = [SelectUserForm, TranslatedUserObjectPermissionsForm]
    template_name = 'monitorings/permission_wizard.html'

    def perm_check(self):
        if not self.request.user.has_perm('monitorings.manage_perm',
                                          self.monitoring):
            raise PermissionDenied()

    @cached_property
    def monitoring(self):
        return Monitoring.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, *args, **kwargs):
        context = super(PermissionWizard, self).get_context_data(*args, **kwargs)
        context['object'] = self.monitoring
        return context

    def get_form_kwargs(self, step=None):
        kw = super(PermissionWizard, self).get_form_kwargs(step)
        self.perm_check()
        if step == '1':
            user_pk = self.storage.get_step_data('0').get('0-user')[0]
            user = get_user_model().objects.get(pk=user_pk)
            kw['user'] = user
            kw['obj'] = self.monitoring
        return kw

    def get_success_message(self):
        return _("Permissions to {monitoring} updated!").format(monitoring=self.object)

    def done(self, form_list, *args, **kwargs):
        form_list[1].save_obj_perms()
        self.object = form_list[1].obj
        messages.success(self.request, self.get_success_message())
        url = reverse('monitorings:perm', kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(url)


class MonitoringPermissionView(RaisePermissionRequiredMixin, SelectRelatedMixin, DetailView):
    model = Monitoring
    template_name_suffix = '_permissions'
    select_related = ['user', ]
    permission_required = 'monitorings.manage_perm'

    def get_context_data(self,  **kwargs):
        context = super(MonitoringPermissionView, self).get_context_data(**kwargs)
        context['user_list'], context['index'] = self.object.permission_map()
        return context


class MonitoringUpdatePermissionView(RaisePermissionRequiredMixin, SelectRelatedMixin, FormView):
    form_class = SaveTranslatedUserObjectPermissionsForm
    template_name = 'monitorings/monitoring_form.html'
    permission_required = 'monitorings.manage_perm'

    def get_permission_object(self):
        return self.get_monitoring()

    def get_user(self):
        if not getattr(self, 'user', None):
            self.user = get_object_or_404(get_user_model(), id=self.kwargs['user_pk'])
        return self.user

    def get_monitoring(self):
        if not getattr(self, 'monitoring', None):
            self.monitoring = get_object_or_404(Monitoring, slug=self.kwargs['slug'])
        return self.monitoring

    def get_context_data(self, **kwargs):
        context = super(MonitoringUpdatePermissionView, self).get_context_data(**kwargs)
        context['object'] = self.get_monitoring()
        return context

    def get_form_kwargs(self):
        kw = super(MonitoringUpdatePermissionView, self).get_form_kwargs()
        kw.update({'user': self.get_user(), 'obj': self.get_monitoring()})
        return kw

    def get_success_message(self):
        return (_("Permissions to {monitoring} of {user} updated!").
                format(monitoring=self.monitoring, user=self.user))

    def form_valid(self, form):
        form.save_obj_perms()
        messages.success(self.request, self.get_success_message())
        url = reverse('monitorings:perm', kwargs={'slug': self.get_monitoring().slug})
        return HttpResponseRedirect(url)


class MonitoringAssignView(RaisePermissionRequiredMixin, FilterView):
    model = Institution
    filterset_class = InstitutionFilter
    permission_required = 'monitorings.change_monitoring'
    template_name = 'monitorings/institution_assign.html'
    paginate_by = 50

    def get_queryset(self):
        qs = super(MonitoringAssignView, self).get_queryset()
        return (qs.exclude(case__monitoring=self.monitoring.pk).
                with_case_count().
                select_related('jst'))

    def get_permission_object(self):
        return self.monitoring

    @cached_property
    def monitoring(self):
        return get_object_or_404(Monitoring, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(MonitoringAssignView, self).get_context_data(**kwargs)
        context['monitoring'] = self.monitoring
        return context

    def get_filterset_kwargs(self, filterset_class):
        kw = super(MonitoringAssignView, self).get_filterset_kwargs(filterset_class)
        return kw

    def post(self, request, *args, **kwargs):
        if request.POST.get('all', 'no') == 'yes':
            qs = self.get_filterset(self.get_filterset_class()).qs
        else:
            ids = request.POST.getlist('to_assign')
            qs = Institution.objects.filter(pk__in=ids)
        qs = qs.exclude(case__monitoring=self.monitoring.pk)
        num = self.monitoring.case_set.count()
        count = Case.objects.filter(monitoring=self.monitoring).count() or 1

        for institution in qs:
            postfix = " #%d" % (num + count,)
            Letter.send_new_case(user=self.request.user,
                                 monitoring=self.monitoring,
                                 postfix=postfix,
                                 institution=institution,
                                 text=self.monitoring.template)
            count += 1
        msg = _("%(count)d institutions was assigned " +
                "to %(monitoring)s. The requests was sent.") % \
              {'count': count, 'monitoring': self.monitoring}
        messages.success(self.request, msg)
        url = reverse('monitorings:assign', kwargs={'slug': self.monitoring.slug})
        return HttpResponseRedirect(url)


class MonitoringAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Monitoring.objects
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.all()


class UserMonitoringAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = (get_user_model().objects.
              annotate(case_count=Count('case')).
              filter(case_count__gt=0).all())
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.all()
