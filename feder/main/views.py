from django.views.generic import TemplateView

from feder.monitorings.models import Monitoring


class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['monitoring_list'] = Monitoring.objects.order_by('created').all()[:16]
        return context
