from functools import partial

from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
from braces.views import FormValidMessageMixin, SelectRelatedMixin, UserFormKwargsMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from formtools.preview import FormPreview

from feder.cases.models import Case
from feder.main.mixins import AttrPermissionRequiredMixin, RaisePermissionRequiredMixin

from .filters import LetterFilter
from .forms import LetterForm, ReplyForm
from .models import Letter

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
                       CreateMessageMixin, CreateView):
    model = Letter
    form_class = LetterForm
    permission_required = 'monitorings.add_letter'

    def get_case(self):
        self.case = get_object_or_404(Case.objects.select_related('monitoring'),
                                      pk=self.kwargs['case_pk'])
        return self.case

    def get_permission_object(self):
        return self.get_case().monitoring

    def get_form_kwargs(self):
        kw = super(LetterCreateView, self).get_form_kwargs()
        kw['case'] = self.case
        return kw


class LetterReplyView(FormPreview):
    form_template = 'letters/letter_reply.html'
    preview_template = 'letters/letter_preview.html'
    model = Letter
    form_class = ReplyForm

    # Hack around django-formtools.FormPreview
    @classmethod
    def as_view(cls):
        return login_required(cls(cls.form_class))

    def __init__(self, form):
        self.state = {}

    # Support dynamic form-kwargs
    @property
    def form(self):
        return partial(self.form_class, letter=self.object, user=self.user)

    def unused_name(self, name, *args, **kwargs):
        return name

    # Pass requests to parse_params - see django/django-formtools#22
    def __call__(self, request, *args, **kwargs):
        stage = {
            '1': 'preview',
            '2': 'post',
        }.get(request.POST.get(self.unused_name('stage')), 'preview')
        self.parse_params(request, *args, **kwargs)
        try:
            method = getattr(self, stage + '_' + request.method.lower())
        except AttributeError:
            raise Http404
        return method(request)

    def post_post(self, request):
        """
        Validates the POST data. If valid, calls done(). Else, redisplays form.
        """
        form = self.form(request.POST, auto_id=self.get_auto_id())
        if form.is_valid():
            if not self._check_security_hash(
                    request.POST.get(self.unused_name('hash'), ''),
                    request, form):
                return self.failed_hash(request)
            return self.done(request, form)
        else:
            return render(request, self.form_template, self.get_context(request, form))

    # Logic & business
    def parse_params(self, request, *args, **kwargs):
        self.user = request.user
        self.object = self.model.objects.select_related('case__monitoring').get(pk=kwargs['pk'])
        if not request.user.has_perm('monitorings.reply', self.object.case.monitoring):
            raise PermissionDenied()

    def done(self, request, form):
        form.save()
        return redirect(form.instance.get_absolute_url())

    def get_context(self, *args, **kwargs):
        context = super(LetterReplyView, self).get_context(*args, **kwargs)
        context['object'] = self.object
        return context

    def get_form_valid_message(self):
        return _("Reply to {letter} send!").format(monitoring=self.object)


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
