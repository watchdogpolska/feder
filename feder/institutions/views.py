from django.views.generic import DetailView
from django_filters.views import FilterView
from braces.views import SelectRelatedMixin
from feder.monitorings.models import Monitoring
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


class InstitutionDetailView(DetailView):
    model = Institution

    def get_monitoring_list(self, obj):
        return Monitoring.objects.filter(case__institution=obj).all()

    def get_context_data(self, **kwargs):
        context = super(InstitutionDetailView, self).get_context_data(**kwargs)
        context['monitoring_list'] = self.get_monitoring_list(self.object)
        return context
