from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from feder.monitorings.models import Monitoring
from feder import get_version


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring_list"] = (
            Monitoring.objects.for_user(self.request.user)
            .order_by("-created")
            .all()[:16]
        )
        context["version"] = get_version()
        return context


def handler500(request):
    context = {"request": request}
    try:
        from sentry_sdk import last_event_id

        context["sentry_event_id"] = last_event_id()
    except ImportError:
        pass
    template_name = "500.html"
    return TemplateResponse(request, template_name, context, status=500)
