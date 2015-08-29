from .models import Questionary


def factory_questionary(monitoring):
    return Questionary.objects.create(title="blabla", monitoring=monitoring)
