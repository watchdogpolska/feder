from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import (CreateMessageMixin, DeleteMessageMixin,
                        UpdateMessageMixin)
from braces.views import (FormValidMessageMixin, SelectRelatedMixin,
                          UserFormKwargsMixin)
from cached_property import cached_property
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_text
from django.utils.feedgenerator import Atom1Feed, Enclosure
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from feder.cases.models import Case
from feder.main.mixins import (AttrPermissionRequiredMixin,
                               RaisePermissionRequiredMixin)
from feder.monitorings.models import Monitoring

from .filters import LetterFilter
from .forms import LetterForm, ReplyForm
from .mixins import LetterObjectFeedMixin
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


class LetterRssFeed(Feed):
    title = _("Latest letters on whole site")
    link = reverse_lazy("letters:list")
    description = _("Updates on new letters on site including " +
                    "receving and sending in all monitorings.")
    feed_url = reverse_lazy("letters:rss")
    description_template = "letters/_letter_feed_item.html"

    def items(self):
        return Letter.objects.with_feed_items().order_by('-created')[:30]

    def item_title(self, item):
        return item.title

    def item_author_name(self, item):
        return force_text(item.author)

    def item_author_link(self, item):
        return item.author.get_absolute_url()

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified

    def item_categories(self, item):
        return [item.case,
                item.case.monitoring,
                item.case.institution,
                item.case.institution.jst]

    def item_enclosures(self, item):
        if item.eml:
            return Enclosure(
                    length=force_text(0),
                    url=force_text(item.eml.url),
                    mime_type="application/octet-stream"
            )
        return None


class LetterAtomFeed(LetterRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterMonitoringRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Monitoring
    filter_field = 'case__monitoring'
    kwargs_name = 'monitoring_pk'

    def title(self, obj):
        return _("Letter for monitoring %s") % force_text(obj)

    def description(self, obj):
        return _("Archive of letter for cases which involved in monitoring %s") % force_text(obj)


class LetterMonitoringAtomFeed(LetterRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterMonitoringRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterCaseRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Case
    filter_field = 'case'
    kwargs_name = 'case_pk'

    def title(self, obj):
        return _("Letter for case %s") % force_text(obj)

    def description(self, obj):
        return _("Archive of letter for case %s") % force_text(obj)


class LetterCaseAtomFeed(LetterCaseRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterCaseRssFeed.description
    feed_url = reverse_lazy("letters:atom")
