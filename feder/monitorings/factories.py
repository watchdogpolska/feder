from .models import Monitoring


def factory_monitoring(user):
    return Monitoring.objects.create(name="Lor", user=user)
