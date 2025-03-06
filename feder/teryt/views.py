from django.views.generic import DetailView, ListView
from teryt_tree.dal_ext.views import CommunityAutocomplete
from teryt_tree.models import JednostkaAdministracyjna
from teryt_tree.rest_framework_ext.serializers import JednostkaAdministracyjnaSerializer
from teryt_tree.rest_framework_ext.viewsets import JednostkaAdministracyjnaFilter

try:
    from django_filters import rest_framework as filters
except ImportError:  # Back-ward compatible for django-rest-framework<3.7
    from rest_framework import filters

from rest_framework import viewsets

from feder.teryt.models import JST


class JSTDetailView(DetailView):
    model = JST

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_qs"] = (
            context["object"].case_qs().for_user(self.request.user).all()
        )
        context["case_qs_count"] = context["case_qs"].count()
        context["institution_qs"] = (
            context["object"].institution_qs().for_user(self.request.user).all()
        )
        context["institution_qs_count"] = context["institution_qs"].count()
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
        return (
            JST.objects.filter(active=True)
            .select_related("category", "parent", "parent__parent")
            .order_by("name")
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
        result_parent = f", {result.parent}" if result.parent else ""
        result_parent_parent = (
            f", {result.parent.parent}"
            if result.parent and result.parent.parent
            else ""
        )
        return (
            f"{result.name} ({result.id}, {result.category}"
            + f"{result_parent}{result_parent_parent})"
        )


class CustomCommunityAutocomplete(JSTAutocompleteMixin, CommunityAutocomplete):
    def get_base_queryset(self):
        return super().get_base_queryset().community()


class JSTAutocomplete(JSTAutocompleteMixin, CommunityAutocomplete):
    pass


class TerytViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        JednostkaAdministracyjna.objects.select_related("category")
        .prefetch_related("children")
        .all()
    )
    serializer_class = JednostkaAdministracyjnaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = JednostkaAdministracyjnaFilter
