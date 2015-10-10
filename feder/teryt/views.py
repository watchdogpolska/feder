from django.views.generic import DetailView, ListView

from feder.teryt.models import JednostkaAdministracyjna


class JSTDetailView(DetailView):
    model = JednostkaAdministracyjna
    template_name = 'teryt/jst_detail.html'


class JSTListView(ListView):
    model = JednostkaAdministracyjna

    def get_queryset(self, *args, **kwargs):
        qs = super(JSTListView, self).get_queryset(*args, **kwargs)
        return qs.voivodeship()
