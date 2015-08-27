from atom.views import ActionMessageMixin, ActionView, CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import (
    FormValidMessageMixin,
    LoginRequiredMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    UserFormKwargsMixin
)
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django_filters.views import FilterView
from formtools.wizard.views import SessionWizardView

from feder.main.mixins import AttrPermissionRequiredMixin, RaisePermissionRequiredMixin
from feder.monitorings.models import Monitoring
from feder.tasks.forms import AnswerFormSet, MultiTaskForm

from .filters import QuestionaryFilter
from .forms import BoolQuestionForm, QuestionaryForm, QuestionForm
from .models import Question, Questionary


class QuestionaryListView(SelectRelatedMixin, FilterView):
    filterset_class = QuestionaryFilter
    model = Questionary
    select_related = ['monitoring', ]
    paginate_by = 25

    def get_filterset_kwargs(self, *args, **kwargs):
        kwargs = super(QuestionaryListView, self).get_filterset_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class QuestionaryDetailView(PrefetchRelatedMixin, DetailView):
    model = Questionary
    prefetch_related = ['question_set']

    def get_context_data(self, **kwargs):
        context = super(QuestionaryDetailView, self).get_context_data(**kwargs)
        context['answer_forms'] = AnswerFormSet(questionary=self.object)
        return context


class QuestionaryCreateView(LoginRequiredMixin, RaisePermissionRequiredMixin,
                            UserFormKwargsMixin, CreateMessageMixin, CreateView):
    model = Questionary
    form_class = QuestionaryForm
    permission_required = 'monitorings.add_questionary'
    raise_exception = True

    def get_monitoring(self):
        self.monitoring = get_object_or_404(Monitoring, pk=self.kwargs['monitoring'])
        return self.monitoring

    def get_permission_object(self):
        return self.get_monitoring()

    def get_form_kwargs(self, *args, **kwargs):
        kw = super(QuestionaryCreateView, self).get_form_kwargs(*args, **kwargs)
        kw['monitoring'] = self.monitoring
        return kw


class QuestionaryUpdateView(LoginRequiredMixin, AttrPermissionRequiredMixin, UserFormKwargsMixin,
                            UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Questionary
    form_class = QuestionaryForm
    permission_required = 'monitorings.change_questionary'
    permission_attribute = 'monitoring'
    raise_exception = True


class QuestionaryDeleteView(LoginRequiredMixin, AttrPermissionRequiredMixin,
                            SelectRelatedMixin, DeleteMessageMixin, DeleteView):
    model = Questionary
    permission_required = 'monitorings.delete_questionary'
    permission_attribute = 'monitoring'
    select_related = ['monitoring']
    raise_exception = True

    def get_success_url(self):
        return self.object.monitoring.get_absolute_url()


class QuestionWizard(SessionWizardView):
    form_list = [QuestionForm, BoolQuestionForm]
    template_name = 'questionaries/question_wizard.html'

    def perm_check(self):
        if not self.request.user.has_perm('monitorings.change_questionary',
                                          self.questionary.monitoring):
            raise PermissionDenied()
        if self.questionary.lock:
            raise PermissionDenied("This questionary are locked to edit")

    def get_form_kwargs(self, step):
        self.questionary = get_object_or_404(Questionary, pk=self.kwargs['pk'])
        self.perm_check()
        kwargs = {'user': self.request.user}
        if step == '0':
            kwargs.update({'questionary': self.questionary})
        if step == '1':
            data = self.storage.get_step_data('0')
            kwargs.update({'genre': data.get('0-genre')})
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionWizard, self).get_context_data(*args, **kwargs)
        context['object'] = self.questionary
        context['headline'] = _('Create question')
        return context

    def done(self, form_list, **kwargs):
        obj = list(form_list)[0].save(list(form_list)[1].cleaned_data)
        return redirect(obj.questionary)


class QuestionMoveView(LoginRequiredMixin, AttrPermissionRequiredMixin,
                       ActionMessageMixin, SelectRelatedMixin, ActionView):
    model = Question
    template_name_suffix = '_move'
    direction = None
    select_related = ['questionary__monitoring', ]
    permission_required = 'monitorings.change_questionary'
    permission_attribute = 'questionary__monitoring'
    change = {'up': -1, 'down': +1}

    def action(self, *args, **kwargs):
        self.object.position = F('position') + self.change[self.direction]
        self.object.save()

    def get_success_message(self):
        return _("Question {object} moved!").format(object=self.object)

    def get_success_url(self):
        return self.object.questionary.get_absolute_url()


class TaskMultiCreateView(LoginRequiredMixin,
                          RaisePermissionRequiredMixin,
                          UserFormKwargsMixin,
                          FormValidMessageMixin,
                          SingleObjectTemplateResponseMixin,
                          SingleObjectMixin,
                          FormView):
    model = Questionary
    form_class = MultiTaskForm
    template_name_suffix = '_form'
    permission_required = 'monitorings.add_tasks'
    raise_exception = True

    def get_permission_object(self):
        return super(TaskMultiCreateView, self).get_permission_object().monitoring

    def get_form_kwargs(self):
        kwargs = super(TaskMultiCreateView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs.update({'questionary': self.object})
        return kwargs

    def get_form_valid_message(self):
        return _("Tasks for {questionary} created!").format(questionary=self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(TaskMultiCreateView, self).form_valid(form, *args, **kwargs)
