# Create your views here.
from atom.views import ActionMessageMixin, ActionView, DeleteMessageMixin
from braces.views import (
    FormValidMessageMixin,
    LoginRequiredMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin
)
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from feder.monitorings.models import Monitoring
from main.mixins import AttrPermissionRequiredMixin, RaisePermissionRequiredMixin

from .filters import AlertFilter
from .forms import AlertForm
from .models import Alert


class MonitoringMixin(object):
    def get_monitoring(self):
        if not getattr(self, 'monitoring', None):
            self.monitoring = get_object_or_404(Monitoring, pk=self.kwargs['monitoring'])
        return self.monitoring

    def get_permission_object(self):
        return self.get_monitoring()


class AlertListView(MonitoringMixin, RaisePermissionRequiredMixin, SelectRelatedMixin, FilterView):
    filterset_class = AlertFilter
    model = Alert
    paginate_by = 25
    select_related = ['solver', 'author', 'monitoring']
    permission_required = 'monitorings.view_alert'

    def get_queryset(self, *args, **kwargs):
        qs = super(AlertListView, self).get_queryset(*args, **kwargs)
        return qs.monitoring(self.get_monitoring())


class AlertDetailView(AttrPermissionRequiredMixin, SelectRelatedMixin, DetailView):
    model = Alert
    select_related = ['solver', 'author', 'monitoring']
    permission_required = 'monitorings.view_alert'
    permission_attribute = 'monitoring'


class AlertCreateView(MonitoringMixin, UserFormKwargsMixin, CreateView):
    model = Alert
    form_class = AlertForm

    def get_form_kwargs(self, *args, **kwargs):
        r = super(AlertCreateView, self).get_form_kwargs(*args, **kwargs)
        r['monitoring'] = self.get_monitoring()
        return r

    def get_context_data(self, **kwargs):
        context = super(AlertCreateView, self).get_context_data(**kwargs)
        context['monitoring'] = self.get_monitoring()
        return context

    def get_form_valid_message(self):
        return _("{object} created!").format(object=self.object)


class AlertUpdateView(AttrPermissionRequiredMixin, UserFormKwargsMixin,
                      FormValidMessageMixin, UpdateView):
    model = Alert
    form_class = AlertForm
    permission_required = 'monitorings.change_alert'
    permission_attribute = 'monitoring'

    def get_form_valid_message(self):
        return _("{object} updated!").format(object=self.object)


class AlertDeleteView(AttrPermissionRequiredMixin, DeleteMessageMixin,
                      DeleteView):
    model = Alert
    permission_required = 'monitorings.delete_alert'
    permission_attribute = 'monitoring'

    def get_success_message(self):
        return _("{object} deleted!").format(object=self.object)

    def get_success_url(self):
        return self.object.monitoring


class AlertStatusView(AttrPermissionRequiredMixin, ActionMessageMixin, ActionView):
    template_name_suffix = '_switch'
    permission_required = 'monitorings.delete_alert'
    permission_attribute = 'monitoring'

    def get_queryset(self):
        return Alert.objects.filter(pk=self.kwargs['pk'])

    def action(self):
        if not self.object.status:
            self.object.solver = self.request.user
        self.object.status = not self.object.status
        self.object.save()

    def get_success_message(self):
        return "{object} status updated!".format(object=self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()
