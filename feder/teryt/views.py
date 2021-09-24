from django.views.generic import DetailView, ListView
from teryt_tree.dal_ext.views import CommunityAutocomplete

from feder.teryt.models import JST


class JSTDetailView(DetailView):
    model = JST

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_qs"] = (
            context["object"].case_qs().for_user(self.request.user).all()
        )
        context["institution_qs"] = (
            context["object"].institution_qs().for_user(self.request.user).all()
        )
        return context


class JSTListView(ListView):
    model = JST

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.voivodeship()


class JSTAutocompleteMixin:
    def get_base_queryset(self):
        """
        Refactored from CommunityAutocomplete view to use JST model
        instead of JednostkaAdministracyjna.
        additionally select_related "parent" and "parent__parent" has been added
        and filtered only the active records.
        """
        return JST.objects.filter(active=True).select_related(
            "category", "parent", "parent__parent"
        )

    def get_queryset(self):
        qs = self.get_base_queryset()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        county = self.forwarded.get("county", None)
        if county:
            return qs.filter(parent=county)

        return qs

    def get_result_label(self, result):
        return result.get_full_name()


class CustomCommunityAutocomplete(JSTAutocompleteMixin, CommunityAutocomplete):
    def get_base_queryset(self):
        return super().get_base_queryset().community()


class JSTAutocomplete(JSTAutocompleteMixin, CommunityAutocomplete):
    pass
