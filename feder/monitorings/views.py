from django.views.generic import DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin)
from formtools.preview import FormPreview
from django_filters.views import FilterView
from atom.views import DeleteMessageMixin, UpdateMessageMixin
from feder.main.mixins import ExtraListMixin
from feder.cases.models import Case
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


class MonitoringUpdateView(LoginRequiredMixin, UserFormKwargsMixin,
        UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Monitoring
    form_class = MonitoringForm


class MonitoringDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Monitoring
    success_url = reverse_lazy('monitorings:list')
