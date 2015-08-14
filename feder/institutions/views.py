from django.views.generic import DetailView
from django_filters.views import FilterView
from django.core.paginator import Paginator, EmptyPage
from braces.views import SelectRelatedMixin, PrefetchRelatedMixin
from feder.cases.models import Case
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


class InstitutionDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = Institution
    prefetch_related = ['tags']
    select_related = []
    paginate_by = 5

    def paginator(self, obj_list):
        paginator = Paginator(obj_list, self.paginate_by)
        try:
            return paginator.page(self.kwargs.get('page', 1))
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            return paginator.page(paginator.num_pages)

    @staticmethod
    def get_case_list(obj):
        return (Case.objects.filter(institution=obj).
            select_related('monitoring').
            prefetch_related('task_set').
            order_by('monitoring').all())

    def get_context_data(self, **kwargs):
        context = super(InstitutionDetailView, self).get_context_data(**kwargs)
        case_list = self.get_case_list(self.object)
        context['case_list'] = self.paginator(case_list)
        return context
