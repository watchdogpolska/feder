from django.views.generic import DetailView, ListView

from .models import JednostkaAdministracyjna


class JSTDetailView(DetailView):
    model = JednostkaAdministracyjna
    template_name = 'teryt/jst_detail.html'


class JednostkaAdministracyjnaListView(ListView):
    model = JednostkaAdministracyjna

    def get_queryset(self, *args, **kwargs):
        qs = super(JednostkaAdministracyjnaListView, self).get_queryset(*args, **kwargs)
        return qs.voivodeship()
