from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import FormValidMessageMixin, SelectRelatedMixin, UserFormKwargsMixin
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from feder.cases.models import Case
from feder.main.mixins import AttrPermissionRequiredMixin, RaisePermissionRequiredMixin

from .filters import LetterFilter
from .forms import LetterForm, ReplyForm
from .models import Letter
from cached_property import cached_property


_("Letters index")


class LetterListView(UserKwargFilterSetMixin, SelectRelatedMixin, FilterView):
    filterset_class = LetterFilter
    model = Letter
    select_related = ['author_user', 'author_institution', 'case__institution']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(LetterListView, self).get_queryset(*args, **kwargs)
        return qs.attachment_count()


class LetterDetailView(SelectRelatedMixin, DetailView):
    model = Letter
    select_related = ['author_institution', 'author_user', 'case__monitoring']


class LetterCreateView(RaisePermissionRequiredMixin, UserFormKwargsMixin,
                       CreateMessageMixin, FormValidMessageMixin, CreateView):
    model = Letter
    form_class = LetterForm
    permission_required = 'monitorings.add_letter'

    @cached_property
    def case(self):
        return get_object_or_404(Case.objects.select_related('monitoring'),
                                 pk=self.kwargs['case_pk'])

    def get_permission_object(self):
        return self.case.monitoring

    def get_form_kwargs(self):
        kw = super(LetterCreateView, self).get_form_kwargs()
        kw['case'] = self.case
        return kw


class LetterReplyView(RaisePermissionRequiredMixin, UserFormKwargsMixin,
                      FormValidMessageMixin, CreateView):
    template_name = 'letters/letter_reply.html'
    model = Letter
    form_class = ReplyForm
    permission_required = 'monitorings.reply'

    @cached_property
    def letter(self):
        return get_object_or_404(Letter.objects.select_related('case__monitoring'),
                                 pk=self.kwargs['pk'])

    def get_permission_object(self):
        return self.letter.case.monitoring

    def get_form_kwargs(self):
        kw = super(LetterReplyView, self).get_form_kwargs()
        kw['letter'] = self.letter
        return kw

    def get_context_data(self, **kwargs):
        context = super(LetterReplyView, self).get_context_data(**kwargs)
        context['object'] = self.letter
        return context

    def get_form_valid_message(self):
        return _("Reply {reply} to {letter} saved and send!").format(
                letter=self.letter,
                reply=self.object)


class LetterUpdateView(AttrPermissionRequiredMixin, UserFormKwargsMixin,
                       UpdateMessageMixin, FormValidMessageMixin, UpdateView):
    model = Letter
    form_class = LetterForm
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.change_letter'


class LetterDeleteView(AttrPermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Letter
    permission_attribute = 'case__monitoring'
    permission_required = 'monitorings.delete_letter'

    def get_success_url(self):
        return self.object.case.get_absolute_url()
