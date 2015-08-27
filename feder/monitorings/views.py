from atom.views import DeleteMessageMixin, UpdateMessageMixin
from braces.views import FormValidMessageMixin, LoginRequiredMixin, SelectRelatedMixin, UserFormKwargsMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from formtools.preview import FormPreview
from guardian.mixins import PermissionRequiredMixin

from feder.cases.models import Case
from feder.main.mixins import ExtraListMixin

from .filters import MonitoringFilter
from .forms import CreateMonitoringForm, MonitoringForm
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


class MonitoringUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UserFormKwargsMixin,
                           UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Monitoring
    form_class = MonitoringForm
    permission_required = 'monitorings.change_monitoring'
    raise_exception = True


class MonitoringDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteMessageMixin,
                           DeleteView):
    model = Monitoring
    success_url = reverse_lazy('monitorings:list')
    permission_required = 'monitorings.delete_monitoring'
    raise_exception = True
