from autoslug.fields import AutoSlugField
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

_('Institution index')

from feder.teryt.models import JST

class InstitutionQuerySet(models.QuerySet):

    def with_case_count(self):
        return self.annotate(case_count=models.Count('case'))

    def area(self, jst):
        return self.filter(jst__tree_id=jst.tree_id,
                           jst__lft__range=(jst.lft, jst.rght))


@python_2_unicode_compatible
class Institution(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"), unique=True)
    tags = models.ManyToManyField('Tag',
                                  null=True,
                                  blank=True,
                                  verbose_name=_("Tag"))
    address = models.EmailField(verbose_name=_("E-mail"),
                                help_text=_("E-mail address used to contact with institutions"))
    jst = models.ForeignKey(JST,
                            limit_choices_to={'category__level': 3},
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


@python_2_unicode_compatible
class Email(models.Model):
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"))
    email = models.EmailField(verbose_name=_("E-mail"), unique=True)

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    def __str__(self):
        return self.email


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=15, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:list') + "?tags=" + str(self.pk)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
