from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, FormView
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import SingleObjectTemplateResponseMixin, SingleObjectMixin
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin, PrefetchRelatedMixin)
from django.core.urlresolvers import reverse_lazy
from django_filters.views import FilterView
from atom.views import DeleteMessageMixin, ActionView, ActionMessageMixin
from formtools.wizard.views import SessionWizardView
from django.db.models import F
from feder.tasks.forms import MultiTaskForm
from .models import Questionary, Question
from .filters import QuestionaryFilter
from .forms import QuestionaryForm, QuestionForm, BoolQuestionForm, AnswerFormSet


class QuestionaryListView(SelectRelatedMixin, FilterView):
    filterset_class = QuestionaryFilter
    model = Questionary
    # select_related = ['', ]
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(QuestionaryListView, self).get_queryset(*args, **kwargs)
        return qs

"""
class QuestionaryListView(SelectRelatedMixin, ListView):
    model = Questionary
    select_related = ['']
"""


class QuestionaryDetailView(PrefetchRelatedMixin, DetailView):
    model = Questionary
    prefetch_related = ['question_set']

    def get_context_data(self, **kwargs):
        context = super(QuestionaryDetailView, self).get_context_data(**kwargs)
        context['answer_forms'] = AnswerFormSet(self.object)
        return context


class QuestionaryCreateView(LoginRequiredMixin, UserFormKwargsMixin, CreateView):
    model = Questionary
    form_class = QuestionaryForm

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)


class QuestionaryUpdateView(LoginRequiredMixin, UserFormKwargsMixin,  FormValidMessageMixin,
        UpdateView):
    model = Questionary
    form_class = QuestionaryForm

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class QuestionaryDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Questionary
    success_url = reverse_lazy('questionaries:list')

    def get_success_message(self):
        return _("{0} deleted!").format(self.object)


class QuestionWizard(SessionWizardView):
    form_list = [QuestionForm, BoolQuestionForm]
    template_name = 'questionaries/question_wizard.html'

    def get_form_kwargs(self, step):
        if step == '0':
            return {'questionary': get_object_or_404(Questionary, pk=self.kwargs['pk'])}
        if step == '1':
            data = self.storage.get_step_data('0')
            return {'genre': data.get('0-genre')}
        return {}

    def done(self, form_list, **kwargs):
        obj = form_list[0].save(form_list[1].cleaned_data)
        return redirect(obj.questionary)


class QuestionMoveView(ActionMessageMixin, ActionView):
    model = Question
    template_name_suffix = '_move'
    direction = None
    change = {'up': +1, 'down': -1}

    def action(self, *args, **kwargs):
        self.object.position = F('position') + self.change[self.direction]
        self.object.save()

    def get_success_message(self):
        return _("{0} moved!").format(self.object)

    def get_success_url(self):
        return self.object.questionary.get_absolute_url()


class TaskMultiCreateView(LoginRequiredMixin, UserFormKwargsMixin, FormValidMessageMixin,
       SingleObjectTemplateResponseMixin, SingleObjectMixin, FormView):
    model = Questionary
    form_class = MultiTaskForm
    template_name_suffix = '_form'

    def get_form_kwargs(self):
        kwargs = super(TaskMultiCreateView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs.update({'questionary': self.object})
        return kwargs

    def get_form_valid_message(self):
        return _("Tasks for {object} created!").format(object=self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(TaskMultiCreateView, self).form_valid(form, *args, **kwargs)
