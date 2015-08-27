import django_filters

from .models import JednostkaAdministracyjna


class JSTModelChoice(django_filters.ModelChoiceFilter):
    model = JednostkaAdministracyjna

    @staticmethod
    def filter__area(queryset, value):
        return queryset.filter(jst__tree_id=value.tree_id, jst__lft__range=(value.lft, value.rght))

    def get_queryset(self):
        qs = self.model.objects.select_related('category')
        if self.level:
            qs = qs.filter(category__level=self.level)
        return qs

    def __init__(self, level=None, *args, **kwargs):
        self.level = level
        kwargs['action'] = self.filter__area
        kwargs['queryset'] = self.get_queryset()
        super(JSTModelChoice, self).__init__(*args, **kwargs)

    def limit_parent(self, value):
        qs = self.field.queryset
        self.field.queryset = qs.filter(parent=value)
