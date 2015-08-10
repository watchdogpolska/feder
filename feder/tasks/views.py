from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin)
from django.core.urlresolvers import reverse_lazy
from django_filters.views import FilterView
from atom.views import DeleteMessageMixin
from .models import Task
from .filters import TaskFilter
from .forms import TaskForm, MultiTaskForm


class TaskListView(SelectRelatedMixin, FilterView):
    filterset_class = TaskFilter
    model = Task
    select_related = ['case', 'questionary']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(TaskListView, self).get_queryset(*args, **kwargs)
        return qs

"""
class TaskListView(SelectRelatedMixin, ListView):
    model = Task
    select_related = ['']
"""


class TaskDetailView(SelectRelatedMixin, DetailView):
    model = Task
    select_related = ['case', 'questionary']


class TaskCreateView(LoginRequiredMixin, UserFormKwargsMixin, CreateView):
    model = Task
    form_class = TaskForm

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)


class TaskUpdateView(LoginRequiredMixin, UserFormKwargsMixin,  FormValidMessageMixin,
        UpdateView):
    model = Task
    form_class = TaskForm

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class TaskDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('tasks:list')

    def get_success_message(self):
        return _("{0} deleted!").format(self.object)


def fill_survey(request, pk):
    pass
