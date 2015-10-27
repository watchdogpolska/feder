from django.views.generic import DetailView, ListView

from feder.teryt.models import JST


class JSTDetailView(DetailView):
    model = JST


class JSTListView(ListView):
    model = JST

    def get_queryset(self, *args, **kwargs):
        qs = super(JSTListView, self).get_queryset(*args, **kwargs)
        return qs.voivodeship()
