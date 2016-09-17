from autoslug.fields import AutoSlugField
from cached_property import cached_property
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from feder.teryt.models import JST

_('Institution index')


class InstitutionQuerySet(models.QuerySet):

    def with_case_count(self):
        return self.annotate(case_count=models.Count('case'))

    def area(self, jst):
        return self.filter(jst__tree_id=jst.tree_id,
                           jst__lft__range=(jst.lft, jst.rght))

    def with_accurate_email(self):
        return self.prefetch_related('email_set')

    def with_any_email(self):
        return self.annotate(email_count=Count('email')).filter(email_count__gte=1)


@python_2_unicode_compatible
class Institution(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    tags = models.ManyToManyField('Tag',
                                  blank=True,
                                  verbose_name=_("Tag"))
    jst = models.ForeignKey(JST,
                            verbose_name=_('Unit of administrative division'),
                            db_index=True)
    objects = InstitutionQuerySet.as_manager()

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institution")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:details', kwargs={'slug': self.slug})

    @cached_property
    def accurate_email(self):
        try:
            self._prefetched_objects_cache['email']
            return max(self.email_set.all(), key=(lambda x: (x.priority, x.created)))
        except (ValueError):  # max() arg is an empty sequence
            return None
        except (AttributeError, KeyError):
            try:
                return self.email_set.order_by('-priority', 'created')[:1].get()
            except Email.DoesNotExist:
                return None


@python_2_unicode_compatible
class Email(TimeStampedModel):
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"))
    email = models.EmailField(verbose_name=_("E-mail"), unique=True)
    priority = models.SmallIntegerField(verbose_name=_("Priority of usage"),
                                        default=0,
                                        help_text=_("Respect of confidence"))

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")
        unique_together = (('institution', 'email', ))
        ordering = ['priority', 'institution', ]

    def __str__(self):
        return self.email


class TagQuerySet(models.QuerySet):
    def used(self):
        return (self.annotate(institution_count=Count('institution')).
                filter(institution_count__gte=1))


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=15, unique=True, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"))
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:list') + "?tags=" + str(self.pk)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name', ]
