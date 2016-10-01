from autoslug.fields import AutoSlugField
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


@python_2_unicode_compatible
class Institution(TimeStampedModel):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    tags = models.ManyToManyField('Tag',
                                  blank=True,
                                  verbose_name=_("Tag"))
    jst = models.ForeignKey(JST,
                            verbose_name=_('Unit of administrative division'),
                            db_index=True)
    email = models.EmailField(verbose_name=_("Email of institution"))
    objects = InstitutionQuerySet.as_manager()

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institution")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:details', kwargs={'slug': self.slug})


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
