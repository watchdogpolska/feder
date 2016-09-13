from autoslug.fields import AutoSlugField
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Prefetch
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from feder.institutions.models import Institution
from feder.monitorings.models import Monitoring


class CaseQuerySet(models.QuerySet):

    def with_letter_count(self):
        return self.annotate(letter_count=models.Count('letter'))

    def area(self, jst):
        return self.filter(institution__jst__tree_id=jst.tree_id,
                           institution__jst__lft__range=(jst.lft, jst.rght))

    def with_milestone(self):
        from feder.letters.models import Letter
        queryset = Letter.objects.for_milestone().all()
        return self.prefetch_related(Prefetch(lookup='letter_set',
                                              queryset=queryset,
                                              to_attr='milestone'))

    def by_msg(self, message):
        email_object = message.get_email_object()
        address = [message.to_addresses]
        if 'Envelope-To' in email_object:
            address += [email_object.get('Envelope-To'), ]
        return self.filter(email__in=address)


class Case(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    monitoring = models.ForeignKey(Monitoring, verbose_name=_("Monitoring"))
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"))
    email = models.CharField(max_length=75, db_index=True, unique=True)
    objects = CaseQuerySet.as_manager()

    class Meta:
        verbose_name = _("Case")
        verbose_name_plural = _("Case")
        ordering = ['created', ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cases:details', kwargs={'slug': self.slug})

    def update_email(self, commit=True):
        self.email = settings.CASE_EMAIL_TEMPLATE.format(pk=self.pk)
        if commit:
            self.save()


@receiver(post_save, sender=Case)
def my_callback(sender, instance, *args, **kwargs):
    if not instance.email:
        instance.update_email()



