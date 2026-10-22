from allauth.account.views import LoginView, SignupView
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from feder.cases.models import Case
from feder.institutions.models import Institution
from feder.main.utils import collapse_next_url, next_param_is_nested
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


class CollapseNestedNextMixin:
    """
    Defends the login/signup views against self-referential `?next=` chains:
    already-crawled/cached deep links, or anyone crafting a chain by hand.
    If the incoming `next` is itself nested, 301-redirect to the same page
    with the chain collapsed down to its innermost real target, instead of
    rendering (and thereby propagating) more nested links.
    """

    def get(self, request, *args, **kwargs):
        raw_next = request.GET.get(REDIRECT_FIELD_NAME)
        if next_param_is_nested(raw_next):
            query = request.GET.copy()
            collapsed = collapse_next_url(raw_next, request)
            if collapsed:
                query[REDIRECT_FIELD_NAME] = collapsed
            else:
                query.pop(REDIRECT_FIELD_NAME, None)
            url = request.path
            if query:
                url = f"{url}?{query.urlencode()}"
            return HttpResponsePermanentRedirect(url)
        return super().get(request, *args, **kwargs)


class CleanLoginView(CollapseNestedNextMixin, LoginView):
    pass


class CleanSignupView(CollapseNestedNextMixin, SignupView):
    pass


class RobotsTxtView(TemplateView):
    template_name = "robots.txt"
    content_type = "text/plain"


def handler500(request):
    context = {"request": request}
    try:
        from sentry_sdk import last_event_id

        context["sentry_event_id"] = last_event_id()
    except ImportError:
        pass
    template_name = "500.html"
    return TemplateResponse(request, template_name, context, status=500)
