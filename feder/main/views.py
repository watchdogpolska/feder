from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from feder.cases.models import Case
from feder.institutions.models import Institution
from feder.monitorings.models import Monitoring
from feder.teryt.models import JST


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring_list"] = (
            Monitoring.objects.for_user(self.request.user)
            .order_by("-created")
            .all()[:16]
        )
        context["voivodeship_table"] = self.generate_voivodeship_table()
        return context

    def generate_voivodeship_table(self):
        """
        Generate html table with voivodeships and their
        institutions and cases counts
        """
        voivodeship_list = JST.objects.filter(category__level=1).all().order_by("name")
        table = """
            <table class="table table-bordered compact" style="width: 100%">
            """
        table += """
            <tr>
                <th>Województwo</th>
                <th>Liczba instytucji</th>
                <th>Liczba spraw</th>
            </tr>"""
        for voivodeship in voivodeship_list:
            table += (
                "<tr><td>"
                + voivodeship.name
                + "</td><td class='text-right'>"
                + str(Institution.objects.area(voivodeship).count())
                + "</td><td class='text-right'>"
                + str(Case.objects.area(voivodeship).count())
                + "</td></tr>"
            )
        table += (
            "<tr><td><b>Wszystkie</b></td><td class='text-right'><b>"
            + str(Institution.objects.all().count())
            + "</b></td><td class='text-right'><b>"
            + str(Case.objects.all().count())
            + "</b></td></tr>"
        )
        table += "</table>"
        return mark_safe(table)


def handler500(request):
    context = {"request": request}
    try:
        from sentry_sdk import last_event_id

        context["sentry_event_id"] = last_event_id()
    except ImportError:
        pass
    template_name = "500.html"
    return TemplateResponse(request, template_name, context, status=500)
