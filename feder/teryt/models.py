from django.urls import reverse
from teryt_tree.models import JednostkaAdministracyjna


class JST(JednostkaAdministracyjna):
    def institution_qs(self):
        Institution = self.institution_set.model
        return Institution.objects.area(self)

    def case_qs(self):
        Case = self.institution_set.field.model.case_set.field.model
        return Case.objects.area(self)

    def get_absolute_url(self):
        return reverse("teryt:details", kwargs={"slug": self.slug})

    def get_full_name(self):
        name = "{} ({}, {})".format(self.name, self.id, self.category)
        if self.parent:
            name = "{} / {}".format(self.parent, name)
            if self.parent.parent:
                name = "{} / {}".format(self.parent.parent, name)
        return name

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
