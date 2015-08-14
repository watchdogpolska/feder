from django.views.generic import DetailView, ListView
from .models import JednostkaAdministracyjna


class JSTDetailView(DetailView):
    model = JednostkaAdministracyjna
    template_name = 'teryt/jst_detail.html'

    def get_context_data(self, **kwargs):
        context = super(JSTDetailView, self).get_context_data(**kwargs)
        context['breadcrumbs'] = self.object.get_ancestors().all()
        return context


class JednostkaAdministracyjnaListView(ListView):
    model = JednostkaAdministracyjna

    def get_queryset(self, *args, **kwargs):
        qs = super(JednostkaAdministracyjnaListView, self).get_queryset(*args, **kwargs)
        return qs.voivodeship()
