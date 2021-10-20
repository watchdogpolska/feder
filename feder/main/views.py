from sentry_sdk import last_event_id
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from feder.monitorings.models import Monitoring

class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monitoring_list"] = (
            Monitoring.objects.for_user(self.request.user)
            .order_by("-created")
            .all()[:16]
        )
        return context


def handler500(request):
    context = {
        'request': request,
        'sentry_event_id': last_event_id()
    }
    template_name = '500.html'
    return TemplateResponse(request, template_name, context, status=500)