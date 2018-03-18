from atom.views import (ActionMessageMixin, ActionView, CreateMessageMixin,
                        DeleteMessageMixin, UpdateMessageMixin)
from braces.views import (FormValidMessageMixin, PrefetchRelatedMixin,
                          SelectRelatedMixin, UserFormKwargsMixin)
from cached_property import cached_property
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  UpdateView)
from django_filters.views import FilterView

from feder.cases.models import Case
from feder.main.mixins import (AttrPermissionRequiredMixin,
                               RaisePermissionRequiredMixin)
from .filters import TaskFilter
from .forms import AnswerFormSet, SurveyForm, TaskForm
from .models import Survey, Task

DONE_MESSAGE_TEXT = _("Already done the job. If you want to change the answer - delete answers.")

THANK_TEXT = _("Thank you for your submission. It is approaching us to know the " +
               "truth, by obtaining reliable data.")

EXHAUSTED_TEXT = _("Thank you for your help. Unfortunately, all the tasks " +
                   "for you have been exhausted.")


class TaskListView(SelectRelatedMixin, FilterView):
    filterset_class = TaskFilter
    model = Task
    select_related = ['case', 'questionary']
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['stats'] = self.object_list.survey_stats()
        return context


class TaskDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Task
    select_related = ['case__monitoring', 'case__institution', 'questionary']
    prefetch_related = ['survey_set', 'questionary__question_set']

    def get_user_survey(self):
        try:
            return (self.object.survey_set.with_full_answer().
                    of_user(self.request.user, self.request.light_user).get())
        except Survey.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['formset'] = AnswerFormSet(questionary=self.object.questionary)
        context['user_survey'] = self.get_user_survey()
        return context


class TaskSurveyView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Task
    select_related = ['case__monitoring', 'case__institution', 'questionary', ]
    prefetch_related = ['questionary__question_set']
    template_name_suffix = '_survey'

    def get_context_data(self, **kwargs):
        context = super(TaskSurveyView, self).get_context_data(**kwargs)
        survey_list = (Survey.objects.for_task(self.object).with_user().with_full_answer().all())
        context['survey_list'] = survey_list
        user_survey_list = [x for x in survey_list if x.user == self.request.user]  # TODO: Lazy
        context['user_survey'] = user_survey_list[0] if user_survey_list else None
        return context


class TaskCreateView(RaisePermissionRequiredMixin, UserFormKwargsMixin,
                     CreateMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    permission_required = 'monitorings.add_task'

    @cached_property
    def case(self):
        return get_object_or_404(Case.objects.select_related('monitoring'),
                                 pk=self.kwargs['case'])

    def get_permission_object(self):
        return self.case.monitoring

    def get_form_kwargs(self):
        kw = super(TaskCreateView, self).get_form_kwargs()
        kw['case'] = self.case
        return kw

    def get_context_data(self, **kwargs):
        context = super(TaskCreateView, self).get_context_data(**kwargs)
        context['case'] = self.case
        return context


class TaskUpdateView(AttrPermissionRequiredMixin, UserFormKwargsMixin,
                     UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    permission_required = 'monitorings.change_task'
    permission_attribute = 'case__monitoring'


class TaskDeleteView(AttrPermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('tasks:list')
    permission_required = 'monitorings.delete_task'
    permission_attribute = 'case__monitoring'


class SurveyDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Survey
    slug_url_kwarg = 'task_id'
    slug_field = 'task_id'

    def get_queryset(self, *args, **kwargs):
        qs = super(SurveyDeleteView, self).get_queryset()
        return qs.of_user(self.request.user, self.request.light_user).with_full_answer()

    def get_success_url(self):
        return self.object.task.get_absolute_url()


class SurveySelectView(AttrPermissionRequiredMixin, ActionMessageMixin,
                       SelectRelatedMixin, ActionView):  # TODO: Write test
    model = Survey
    template_name_suffix = '_select'
    select_related = ['task__case__monitoring', ]
    permission_required = 'monitorings.select_survey'
    permission_attribute = 'task__case__monitoring'
    direction = None
    change = {'up': 1, 'down': -1}

    def action(self, *args, **kwargs):
        self.object.credibility_update(self.change[self.direction])
        self.object.save()

    def get_success_message(self):
        if self.direction == 'up':
            return _("Survey credibility increased!")
        else:
            return _("Survey credibility decreased!")

    def get_success_url(self):
        return reverse('tasks:survey', kwargs={'pk': self.object.task_id})


class SurveyFillView(FormView):
    template_name = 'tasks/survey_fill.html'
    form_class = SurveyForm
    formset_class = AnswerFormSet

    @cached_property
    def task(self):
        return get_object_or_404(Task, pk=self.kwargs['pk'])

    @cached_property
    def object(self):
        try:
            return Survey.objects.filter(task=self.task).of_user(user=self.request.user,
                                                                 light_user=self.request.light_user).all()[0]
        except IndexError:
            return None

    def get_form_kwargs(self):
        kwargs = super(SurveyFillView, self).get_form_kwargs()
        kwargs['task'] = self.task
        kwargs['instance'] = self.object
        return kwargs

    def get_success_url(self):
        if 'save' in self.request.POST:  # only save
            return self.object.task.get_absolute_url()

        # find next task
        try:
            next_task = self.task.get_next_for_user(self.request.user)
            return next_task.get_absolute_url()
        except Task.DoesNotExist:
            messages.success(self.request, EXHAUSTED_TEXT)
            return self.task.case.monitoring.get_absolute_url()

    @cached_property
    def formset(self):
        return self.formset_class(data=self.request.POST or None,
                                  survey=self.object,
                                  questionary=self.task.questionary)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.formset.is_valid():
            if self.request.user.is_authenticated():
                self.object.user = self.request.user
            else:
                self.object.light_user = self.request.light_user_new
            self.object.save()
            self.formset.save()
            return self.formset_valid(form, self.object, self.formset)
        return self.render_to_response(self.get_context_data())

    def formset_valid(self, form, obj, formset):
        messages.success(self.request, THANK_TEXT)
        obj.save()
        formset.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(SurveyFillView, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        context['object'] = self.object
        context['task'] = self.task
        return context
