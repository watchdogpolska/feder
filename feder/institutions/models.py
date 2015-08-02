from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from autoslug.fields import AutoSlugField
from model_utils.managers import PassThroughManager
from teryt.models import JednostkaAdministracyjna


class JSTQuerySet(models.QuerySet):

    def wojewodztwa(self):
        return self.extra(where=["char_length(id) = 2"])

    def powiaty(self):
        return self.extra(where=["char_length(id) = 4"])

    def gminy(self):
        return self.extra(where=["char_length(id) = 7"])


class JST(JednostkaAdministracyjna):
    objects = PassThroughManager.for_queryset_class(JSTQuerySet)()

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('institutions:list', kwargs={'jst_pk': self.pk})


class InstitutionQuerySet(models.QuerySet):
    def in_jst(self, obj):
        return self.filter(jst__id__startswith=obj)


class Institution(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"))
    tags = models.ManyToManyField('Tag', verbose_name=_("Tag"))
    address = models.EmailField(verbose_name=_("E-mail"))
    jst = models.ForeignKey(JST)
    objects = PassThroughManager.for_queryset_class(InstitutionQuerySet)()

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institution")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:details', kwargs={'slug': self.slug})


class Email(models.Model):
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"))
    email = models.EmailField(verbose_name=_("E-mail"), unique=True)

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    def __str__(self):
        return self.email


class Tag(models.Model):
    name = models.CharField(max_length=15, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from='name', verbose_name=_("Slug"))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:list')+"?tags=" + self.pk
