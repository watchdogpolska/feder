# Create your views here.
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
    UserFormKwargsMixin)
from django.core.urlresolvers import reverse_lazy
from django_filters.views import FilterView
from atom.views import DeleteMessageMixin, CreateMessageMixin, UpdateMessageMixin
from .models import Letter
from .forms import LetterForm
from .filters import LetterFilter

_("Letters index")


class LetterListView(SelectRelatedMixin, FilterView):
    filterset_class = LetterFilter
    model = Letter
    select_related = ['author_user', 'author_institution', 'case__institution']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(LetterListView, self).get_queryset(*args, **kwargs)
        return qs


class LetterDetailView(SelectRelatedMixin, DetailView):
    model = Letter
    select_related = ['author_institution', ]


class LetterCreateView(LoginRequiredMixin, UserFormKwargsMixin,
        CreateMessageMixin, CreateView):
    model = Letter
    form_class = LetterForm


class LetterUpdateView(LoginRequiredMixin, UserFormKwargsMixin, UpdateMessageMixin,
        FormValidMessageMixin, UpdateView):
    model = Letter
    form_class = LetterForm


class LetterDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Letter
    success_url = reverse_lazy('letters:list')
