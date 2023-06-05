import reversion
from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from model_utils.models import TimeStampedModel

from feder.teryt.models import JST

_("Institution index")


class InstitutionQuerySet(models.QuerySet):
    def with_case_count(self):
        return self.annotate(case_count=models.Count("case"))

    def with_jst(self):
        return self.select_related("jst", "jst__parent", "jst__parent__parent")

    def area(self, jst):
        return self.filter(
            jst__tree_id=jst.tree_id, jst__lft__range=(jst.lft, jst.rght)
        )

    def for_user(self, user):  # dummy (at that moment)
        return self

    def active_only(self):
        return self.filter(archival=False)


@reversion.register()
class Institution(TimeStampedModel):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from="name", verbose_name=_("Slug"), unique=True)
    tags = models.ManyToManyField("Tag", blank=True, verbose_name=_("Tag"))
    jst = models.ForeignKey(
        JST,
        on_delete=models.CASCADE,
        verbose_name=_("Unit of administrative division"),
        db_index=True,
    )
    regon = models.CharField(
        max_length=14,
        verbose_name=_("REGON number"),
        unique=True,
        null=True,
        blank=True,
    )
    parents = models.ManyToManyField(
        "self", verbose_name=_("Parent institutions"), blank=True
    )
    extra = JSONField(verbose_name="Unorganized additional information", blank=True)
    email = models.EmailField(verbose_name=_("Email of institution"))
    archival = models.BooleanField(
        default=False,
        verbose_name=_("Archival institution"),
        help_text=_(
            "Archival institution can't be assigned to monitoring or mass mailing."
        ),
    )
    objects = InstitutionQuerySet.as_manager()

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institution")
        ordering = ["name"]

    def __str__(self):
        if self.archival:
            return self.name + _(" (archival)")
        return self.name

    def get_absolute_url(self):
        return reverse("institutions:details", kwargs={"slug": self.slug})

    def get_jst_tree(self):
        """
        Returns voivodeship JST list in order: voivodeship, county, community
        by searching over parents of related JST.
        This operation may be expensive, so in queries it should be used with
        with_jst manager method.
        """
        jst = self.jst
        tree = [jst]
        while jst.parent_id:
            jst = jst.parent
            tree.append(jst)
        tree.reverse()
        return tree

    @property
    def voivodeship(self):
        return self.get_jst_tree()[0]

    @property
    def county(self):
        tree = self.get_jst_tree()
        return tree[1] if len(tree) > 1 else None

    @property
    def community(self):
        tree = self.get_jst_tree()
        return tree[2] if len(tree) > 2 else None


class TagQuerySet(models.QuerySet):
    def used(self):
        return self.annotate(institution_count=Count("institution")).filter(
            institution_count__gte=1
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=250, db_index=True, unique=True, verbose_name=_("Name")
    )
    slug = AutoSlugField(populate_from="name", verbose_name=_("Slug"))
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("institutions:list") + "?tags=" + str(self.pk)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]
