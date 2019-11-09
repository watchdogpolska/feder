from django.apps import AppConfig


class RecordsConfig(AppConfig):
    name = "feder.records"

    def ready(self):
        from . import checks
