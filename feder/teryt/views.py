from django.views.generic import DetailView, ListView

from feder.teryt.models import JST


class JSTDetailView(DetailView):
    model = JST


class JSTListView(ListView):
    model = JST

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.voivodeship()
