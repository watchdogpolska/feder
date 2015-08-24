# -*- coding: utf-8 -*-
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _
from mptt.managers import TreeManager
from model_utils import Choices
from django.core.urlresolvers import reverse
from model_utils.managers import PassThroughManagerMixin
from autoslug import AutoSlugField


class PassThroughTreeManager(PassThroughManagerMixin, TreeManager):
    def with_category(self):
        return self.select_related('category')


class JednostkaAdministracyjnaQuerySet(models.QuerySet):

    def voivodeship(self):
        return self.filter(category__level=1)

    def county(self):
        return self.filter(category__level=2)

    def community(self):
        return self.filter(category__level=3)


class Category(models.Model):
    LEVEL = Choices((1, 'voivodeship', _('voivodeship')),
                    (2, 'county', _('county')),
                    (3, 'community', _('community')))
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='name')

    level = models.IntegerField(choices=LEVEL, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class JednostkaAdministracyjna(MPTTModel):
    id = models.CharField(max_length=7, primary_key=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    name = models.CharField(_('Name'), max_length=36,)
    category = models.ForeignKey(Category)
    slug = AutoSlugField(populate_from='name', unique=True)
    updated_on = models.DateField(verbose_name=_("Updated date"))
    active = models.BooleanField(default=False)
    objects = PassThroughTreeManager.for_queryset_class(JednostkaAdministracyjnaQuerySet)()

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def get_absolute_url(self):
        return reverse('teryt:details', kwargs={'slug': self.slug})

    def institution_qs(self):
        Institution = self.institution_set.model
        return Institution.objects.area(self)

    def case_qs(self):
        Case = self.institution_set.model.case_set.related.related_model
        return Case.objects.area(self)

    def task_qs(self):
        Task = (self.institution_set.model.case_set.related.related_model.
            task_set.related.related_model)
        return Task.objects.select_related('case__monitoring')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('Unit of administrative division')
        verbose_name_plural = _('Units of administrative division')
