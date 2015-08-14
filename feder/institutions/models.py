from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from autoslug.fields import AutoSlugField
from feder.teryt.models import JednostkaAdministracyjna
from model_utils.managers import PassThroughManager


class InstitutionQuerySet(models.QuerySet):
    def with_case_count(self):
        return self.annotate(case_count=models.Count('case'))

    def area(self, jst):
        return self.filter(jst__tree_id=jst.tree_id,
            jst__lft__range=(jst.lft, jst.rght))


class Institution(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    tags = models.ManyToManyField('Tag', verbose_name=_("Tag"))
    address = models.EmailField(verbose_name=_("E-mail"))
    jst = models.ForeignKey(JednostkaAdministracyjna, limit_choices_to={'category__level': 3},
        verbose_name=_('Unit of administrative division'), db_index=True)
    objects = PassThroughManager.for_queryset_class(InstitutionQuerySet)()

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institution")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:details', kwargs={'slug': self.slug})


class Email(models.Model):
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"))
    email = models.EmailField(verbose_name=_("E-mail"), unique=True)

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    def __unicode__(self):
        return self.email


class Tag(models.Model):
    name = models.CharField(max_length=15, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:list') + "?tags=" + str(self.pk)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
