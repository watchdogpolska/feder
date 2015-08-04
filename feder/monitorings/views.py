from django.views.generic import DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin)
from formtools.preview import FormPreview
from django_filters.views import FilterView
from atom.views import DeleteMessageMixin
from .models import Monitoring
from .forms import MonitoringForm, CreateMonitoringForm
from .filters import MonitoringFilter


class MonitoringListView(SelectRelatedMixin, FilterView):
    filterset_class = MonitoringFilter
    model = Monitoring
    select_related = ['user', ]
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(MonitoringListView, self).get_queryset(*args, **kwargs)
        return qs


class MonitoringDetailView(SelectRelatedMixin, DetailView):
    model = Monitoring
    select_related = ['user', ]


class MonitoringCreateView(FormPreview):
    form_template = 'monitorings/monitoring_form.html'
    preview_template = 'monitorings/monitoring_preview.html'
    form_class = CreateMonitoringForm

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
        return _("{0} created!").format(self.object)


class MonitoringUpdateView(LoginRequiredMixin, UserFormKwargsMixin,  FormValidMessageMixin,
        UpdateView):
    model = Monitoring
    form_class = MonitoringForm

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class MonitoringDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Monitoring
    success_url = reverse_lazy('monitorings:list')

    def get_success_message(self):
        return _("{0} deleted!").format(self.object)
