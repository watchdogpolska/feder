from teryt_tree.models import JednostkaAdministracyjna
from django.core.urlresolvers import reverse


class JST(JednostkaAdministracyjna):
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

    def get_absolute_url(self):
        return reverse('teryt:details', kwargs={'slug': self.slug})

    class Meta:
        proxy = True
