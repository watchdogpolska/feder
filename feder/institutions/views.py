from django.views.generic import DetailView
from django_filters.views import FilterView
from braces.views import SelectRelatedMixin, PrefetchRelatedMixin
from feder.cases.models import Case
from feder.main.mixins import ExtraListMixin
from .models import Institution
from .filters import InstitutionFilter


class InstitutionListView(SelectRelatedMixin, FilterView):
    filterset_class = InstitutionFilter
    model = Institution
    select_related = ['jst', 'jst__category']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(InstitutionListView, self).get_queryset(*args, **kwargs)
        return qs.with_case_count()


class InstitutionDetailView(SelectRelatedMixin, ExtraListMixin, PrefetchRelatedMixin, DetailView):
    model = Institution
    prefetch_related = ['tags']
    select_related = []
    extra_list_context = 'case_list'

    @staticmethod
    def get_object_list(obj):
        return (Case.objects.filter(institution=obj).
            select_related('monitoring').
            prefetch_related('task_set').
            order_by('monitoring').all())
