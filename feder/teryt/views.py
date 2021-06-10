from django.views.generic import DetailView, ListView
from teryt_tree.dal_ext.views import CommunityAutocomplete

from feder.teryt.models import JST


class JSTDetailView(DetailView):
    model = JST


class JSTListView(ListView):
    model = JST

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.voivodeship()


class CustomCommunityAutocomplete(CommunityAutocomplete):
    def get_queryset(self):
        """
        Overridden to use JST model instead fo JednostkaAdministracyjna.
        additionally select_related "parent" and "parent__parent" has been added.
        """
        qs = (
            JST.objects.community()
            .select_related("category", "parent", "parent__parent")
            .all()
        )

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        county = self.forwarded.get("county", None)
        if county:
            return qs.filter(parent=county)
        return qs

    def get_result_label(self, result):
        return result.get_full_name()
