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

    class Meta:
        proxy = True
