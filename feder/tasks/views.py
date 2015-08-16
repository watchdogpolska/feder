from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.db.models import Prefetch
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin, PrefetchRelatedMixin)
from atom.views import DeleteMessageMixin, CreateMessageMixin, UpdateMessageMixin
from .models import Task, Survey, Answer
from .filters import TaskFilter
from .forms import TaskForm, AnswerFormSet, SurveyForm


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


class TaskDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Task
    select_related = ['case__monitoring', 'case__institution', 'questionary']
    prefetch_related = ['survey_set', 'questionary__question_set']

    def get_context_data(self, *args, **kwargs):
        context = super(TaskDetailView, self).get_context_data(*args, **kwargs)
        context['formset'] = AnswerFormSet(survey=None, questionary=self.object.questionary)
        try:
            context['user_survey'] = (self.object.survey_set.with_full_answer().
            filter(user=self.request.user).get())
        except Survey.DoesNotExist:
            context['user_survey'] = None
        return context


class TaskSurveyView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Task
    select_related = ['case__monitoring', 'case__institution', 'questionary', ]
    prefetch_related = ['questionary__question_set']
    template_name_suffix = '_survey'

    def get_context_data(self, *args, **kwargs):
        context = super(TaskSurveyView, self).get_context_data(*args, **kwargs)
        survey_list = (Survey.objects.for_task(self.object).with_user().with_full_answer().all())
        context['survey_list'] = survey_list
        user_survey_list = [x for x in survey_list if x.user == self.request.user]  # TODO: Lazy
        context['user_survey'] = user_survey_list[0] if user_survey_list else None
        return context


class TaskCreateView(LoginRequiredMixin, UserFormKwargsMixin, CreateMessageMixin, CreateView):
    model = Task
    form_class = TaskForm


class TaskUpdateView(LoginRequiredMixin, UserFormKwargsMixin, UpdateMessageMixin,
        FormValidMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('tasks:list')


class SurveyDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Survey
    slug_url_kwarg = 'task_id'
    slug_field = 'task_id'

    def get_queryset(self, *args, **kwargs):
        qs = super(SurveyDeleteView, self).get_queryset(*args, **kwargs)
        return qs.filter(user=self.request.user).with_full_answer()

    def get_success_url(self):
        return self.object.task.get_absolute_url()


@login_required
def fill_survey(request, pk):
    context = {}
    task = get_object_or_404(Task, pk=pk)
    context['object'] = task
    form = SurveyForm(data=request.POST or None, task=task, user=request.user)
    context['form'] = form
    if request.POST and form.is_valid():
            obj = form.save(commit=False)
            formset = AnswerFormSet(data=request.POST or None, survey=obj,
                questionary=task.questionary)
            context['formset'] = formset
            if formset.is_valid():
                messages.success(request,
                _("Thank you for your submission. It is approaching us to know the " +
                "truth, by obtaining reliable data."))
                obj.save()
                formset.save()
                return redirect(obj.task)
    else:
        formset = AnswerFormSet(data=request.POST or None, questionary=task.questionary)
        context['formset'] = formset
    return render(request, 'tasks/task_fill.html', context)
