from atom.views import DeleteMessageMixin, UpdateMessageMixin
from atom.ext.guardian.forms import TranslatedUserObjectPermissionsForm
from braces.views import (
    FormValidMessageMixin,
    LoginRequiredMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, DetailView, UpdateView, FormView
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django_filters.views import FilterView
from formtools.preview import FormPreview
from formtools.wizard.views import SessionWizardView
from feder.cases.models import Case
from feder.main.mixins import ExtraListMixin, RaisePermissionRequiredMixin

from .filters import MonitoringFilter
from .forms import (
    CreateMonitoringForm,
    MonitoringForm,
    SelectUserForm,
    SaveTranslatedUserObjectPermissionsForm
)
from .models import Monitoring


class MonitoringListView(SelectRelatedMixin, FilterView):
    filterset_class = MonitoringFilter
    model = Monitoring
    select_related = ['user', ]
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(MonitoringListView, self).get_queryset(*args, **kwargs)
        return qs.with_case_count()


class MonitoringDetailView(SelectRelatedMixin, ExtraListMixin, DetailView):
    model = Monitoring
    select_related = ['user', ]
    paginate_by = 25

    @staticmethod
    def get_object_list(obj):
        return (Case.objects.filter(monitoring=obj).
                select_related('institution').
                prefetch_related('task_set').
                order_by('institution').all())


class MonitoringCreateView(FormPreview):
    form_template = 'monitorings/monitoring_form.html'
    preview_template = 'monitorings/monitoring_preview.html'
    form_class = CreateMonitoringForm

    def __call__(self, request, *args, **kwargs):
        if not request.user.has_perm('monitorings.add_monitoring'):
            raise PermissionDenied()
        return super(MonitoringCreateView, self).__call__(request, *args, **kwargs)

    def __init__(self, form):
        self.state = {}

    @property
    def form(self):
        return self.form_class

    @classmethod
    def as_view(cls):
        return login_required(cls(cls.form_class))

    def get_form_kwargs(self):
        return dict(user=self.request.user, auto_id=self.get_auto_id())

    def get_form(self):
        return self.form(self.request.POST, **self.get_form_kwargs())

    def response_done(self, form, context):
        form.save()
        return HttpResponseRedirect(form.instance.get_absolute_url())

    def done(self, request, cleaned_data):
        self.request = request
        form = self.get_form()
        context = self.get_context(request, form)
        return self.response_done(form, context)

    def get_form_valid_message(self):
        return _("Monitoring {monitoring} created!").format(monitoring=self.object)


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
                                          self.get_monitoring()):
            raise PermissionDenied()

    def get_monitoring(self):
        if not getattr(self, 'monitoring', None):
            self.monitoring = Monitoring.objects.get(slug=self.kwargs['slug'])
        return self.monitoring

    def get_context_data(self, *args, **kwargs):
        context = super(PermissionWizard, self).get_context_data(*args, **kwargs)
        context['object'] = self.get_monitoring()
        return context

    def get_form_kwargs(self, step, *args, **kwargs):
        kw = super(PermissionWizard, self).get_form_kwargs(step, *args, **kwargs)
        self.perm_check()
        if step == '1':
            user_pk = self.storage.get_step_data('0').get('0-user')[0]
            user = get_user_model().objects.get(pk=user_pk)
            kw['user'] = user
            kw['obj'] = self.get_monitoring()
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
    permission_required = 'monitorings.change_monitoring'

    def get_context_data(self, *args, **kwargs):
        context = super(MonitoringPermissionView, self).get_context_data(*args, **kwargs)
        context['user_list'], context['index'] = self.object.permission_map()
        return context


class MonitoringUpdatePermissionView(RaisePermissionRequiredMixin, SelectRelatedMixin, FormView):
    form_class = SaveTranslatedUserObjectPermissionsForm
    template_name = 'monitorings/monitoring_form.html'
    permission_required = 'monitorings.change_monitoring'

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

    def get_context_data(self, *args, **kwargs):
        context = super(MonitoringUpdatePermissionView, self).get_context_data(*args, **kwargs)
        context['object'] = self.get_monitoring()
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kw = super(MonitoringUpdatePermissionView, self).get_form_kwargs(*args, **kwargs)
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
