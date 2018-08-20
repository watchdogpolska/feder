from os import path

from atom.ext.django_filters.views import UserKwargFilterSetMixin
from atom.views import (CreateMessageMixin, DeleteMessageMixin,
                        UpdateMessageMixin, ActionView, ActionMessageMixin)
from braces.views import (FormValidMessageMixin, SelectRelatedMixin,
                          UserFormKwargsMixin, PrefetchRelatedMixin)
from cached_property import cached_property
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.utils.encoding import force_text
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, FormView
from django_filters.views import FilterView
from django_mailbox.models import Message
from extra_views import UpdateWithInlinesView, CreateWithInlinesView

from feder.alerts.models import Alert
from feder.cases.models import Case
from feder.letters.filters import MessageFilter
from feder.letters.formsets import AttachmentInline
from feder.main.mixins import (AttrPermissionRequiredMixin,
                               RaisePermissionRequiredMixin, BaseXSendFileView)
from feder.monitorings.models import Monitoring
from .filters import LetterFilter
from .forms import LetterForm, ReplyForm, AssignMessageForm
from .mixins import LetterObjectFeedMixin
from .models import Letter, Attachment

_("Letters index")


class MixinGzipXSendFile(object):
    def get_sendfile_kwargs(self, context):
        kwargs = super(MixinGzipXSendFile, self).get_sendfile_kwargs(context)
        if kwargs['filename'] and kwargs['filename'].endswith('.gz'):
            kwargs['encoding'] = 'gzip'
            filename = path.basename(kwargs['filename'][:-len('.gz')])
            kwargs['attachment_filename'] = filename
        return kwargs


class LetterListView(UserKwargFilterSetMixin, SelectRelatedMixin, FilterView):
    filterset_class = LetterFilter
    model = Letter
    select_related = ['author_user', 'author_institution', 'record__case__institution']
    paginate_by = 25

    def get_queryset(self):
        qs = super(LetterListView, self).get_queryset()
        return qs.attachment_count()


class LetterDetailView(SelectRelatedMixin, DetailView):
    model = Letter
    select_related = ['author_institution', 'author_user', 'record__case__monitoring']


class LetterMessageXSendFileView(MixinGzipXSendFile, BaseXSendFileView):
    model = Letter
    file_field = 'eml'
    send_as_attachment = True


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
                      FormValidMessageMixin, CreateWithInlinesView):
    template_name = 'letters/letter_reply.html'
    model = Letter
    form_class = ReplyForm
    inlines = [AttachmentInline, ]
    permission_required = 'monitorings.add_draft'

    @cached_property
    def letter(self):
        return get_object_or_404(Letter.objects.select_related('record__case__monitoring'),
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

    def forms_valid(self, form, inlines):
        result = super(LetterReplyView, self).forms_valid(form, inlines)
        if 'send' in self.request.POST:
            self.object.send()
        return result

    def get_form_valid_message(self):
        if self.object.eml:
            return _("Reply {reply} to {letter} saved and send!").format(
                letter=self.letter,
                reply=self.object)
        return _("Reply {reply} to {letter} saved to review!").format(
            letter=self.letter,
            reply=self.object)


class LetterSendView(AttrPermissionRequiredMixin, ActionMessageMixin, ActionView):
    model = Letter
    permission_attribute = 'record__case__monitoring'
    permission_required = 'monitorings.reply'
    template_name_suffix = '_send'

    def action(self):
        self.object.send()

    def get_success_message(self):
        return _("Reply {letter} send to {institution}!").format(
            letter=self.object,
            institution=self.object.case.institution)

    def get_success_url(self):
        return self.object.get_absolute_url()


class LetterUpdateView(AttrPermissionRequiredMixin, UserFormKwargsMixin,
                       UpdateMessageMixin, FormValidMessageMixin, UpdateWithInlinesView):
    model = Letter
    form_class = LetterForm
    inlines = [AttachmentInline, ]
    permission_attribute = 'record__case__monitoring'
    permission_required = 'monitorings.change_letter'


class LetterDeleteView(AttrPermissionRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Letter
    permission_attribute = 'record__case__monitoring'
    permission_required = 'monitorings.delete_letter'

    def delete(self, request, *args, **kwargs):
        result = super(LetterDeleteView, self).delete(request, *args, **kwargs)
        [x.attachment.delete() for x in self.object.attachment_set.all()]  # Delete file
        self.object.attachment_set.all().delete()  # Delete objects
        self.object.eml.delete()  # Delete file
        return result

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

    def item_enclosure_url(self, item):
        return item.eml.url if item.eml else None


class LetterAtomFeed(LetterRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterMonitoringRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Monitoring
    filter_field = 'record__case__monitoring'
    kwargs_name = 'monitoring_pk'

    def title(self, obj):
        return _("Letter for monitoring %s") % force_text(obj)

    def description(self, obj):
        return _("Archive of letter for cases which involved in monitoring %s") % force_text(obj)


class LetterMonitoringAtomFeed(LetterMonitoringRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterMonitoringRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterCaseRssFeed(LetterObjectFeedMixin, LetterRssFeed):
    model = Case
    filter_field = 'record__case'
    kwargs_name = 'case_pk'

    def title(self, obj):
        return _("Letter for case %s") % force_text(obj)

    def description(self, obj):
        return _("Archive of letter for case %s") % force_text(obj)


class LetterCaseAtomFeed(LetterCaseRssFeed):
    feed_type = Atom1Feed
    subtitle = LetterCaseRssFeed.description
    feed_url = reverse_lazy("letters:atom")


class LetterReportSpamView(ActionMessageMixin, ActionView):
    template_name_suffix = '_spam'
    model = Letter

    def get_queryset(self):
        return super(LetterReportSpamView, self).get_queryset().filter(is_spam=Letter.SPAM.unknown)

    def action(self):
        author = None if self.request.user.is_anonymous else self.request.user
        Alert.objects.create(monitoring=self.object.case.monitoring,
                             reason=_("SPAM"),
                             author=author,
                             link_object=self.object)

    def get_success_message(self):
        return _("Thanks for your help. The report was forwarded to responsible persons.")

    def get_success_url(self):
        return self.object.case.get_absolute_url()


class LetterMarkSpamView(RaisePermissionRequiredMixin, ActionMessageMixin, ActionView):
    template_name_suffix = '_mark_spam'
    model = Letter
    permission_required = 'monitorings.spam_mark'
    accept_global_perms = True

    def get_object(self, *args, **kwargs):
        if not hasattr(self, 'object'):
            self.object = super(LetterMarkSpamView, self).get_object(*args, **kwargs)
        return self.object

    def get_permission_object(self):
        return self.get_object().case.monitoring

    def get_queryset(self):
        return super(LetterMarkSpamView, self).get_queryset().filter(is_spam=Letter.SPAM.unknown)

    def action(self):
        if 'valid' in self.request.POST:
            self.object.is_spam = Letter.SPAM.non_spam
        else:
            self.object.is_spam = Letter.SPAM.spam
        self.object.mark_spam_by = self.request.user
        self.object.mark_spam_at = datetime.now()
        self.object.save(update_fields=['is_spam', 'mark_spam_by'])
        Alert.objects.link_object(self.object).update(solver=self.request.user,
                                                      status=True)

    def get_success_message(self):
        if 'valid' in self.request.POST:
            return _("The letter {object} has been marked as valid.").format(object=self.object)
        return _("The message {object} has been marked as spam and hidden.").format(object=self.object)

    def get_success_url(self):
        return self.object.case.get_absolute_url()


class UnrecognizedMessageListView(RaisePermissionRequiredMixin, PrefetchRelatedMixin, FilterView):
    filterset_class = MessageFilter
    model = Message
    prefetch_related = ['attachments']
    paginate_by = 50
    permission_object = None
    permission_required = 'letters.recognize_letter'
    template_name = 'letters/messages/message_filter.html'
    ordering = '-pk'

    def get_queryset(self):
        return super(UnrecognizedMessageListView, self).get_queryset().filter(letter=None)

    def get_context_data(self, **kwargs):
        context = super(UnrecognizedMessageListView, self).get_context_data(**kwargs)
        context['object_list'] = self.update_object_list(context['object_list'])
        return context

    def update_object_list(self, object_list):
        result = []
        for obj in object_list:
            obj.assign_form = AssignMessageForm(message=obj)
            result.append(obj)
        return result


class AssignMessageFormView(PrefetchRelatedMixin, RaisePermissionRequiredMixin, SuccessMessageMixin, FormView):
    model = Message
    form_class = AssignMessageForm
    permission_object = None
    success_url = reverse_lazy('letters:messages_list')
    permission_required = 'letters.recognize_letter'
    template_name = 'letters/messages/message_assign.html'
    success_message = _("Assigned message to case '%(case)s'")

    @cached_property
    def message(self):
        obj = get_object_or_404(self.model, pk=self.kwargs['pk'])
        obj.assign_form = AssignMessageForm(message=obj)
        return obj

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.message
        return super(AssignMessageFormView, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(AssignMessageFormView, self).get_form_kwargs()
        kwargs['message'] = self.message
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(AssignMessageFormView, self).form_valid(form)


class AttachmentXSendFileView(MixinGzipXSendFile, BaseXSendFileView):
    model = Attachment
    file_field = 'attachment'
    send_as_attachment = True

    def get_queryset(self):
        return super(AttachmentXSendFileView, self).get_queryset().for_user(self.request.user)

    def get_sendfile_kwargs(self, context):
        kwargs = super(AttachmentXSendFileView, self).get_sendfile_kwargs(context)
        if kwargs['filename'].endswith('.gz'):
            kwargs['encoding'] = 'gzip'
        return kwargs
