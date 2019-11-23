from django.apps import AppConfig


class ParcelsConfig(AppConfig):
    name = "feder.parcels"

    def ready(self):
        from . import types  # noqa
