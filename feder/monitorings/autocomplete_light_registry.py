import autocomplete_light

from feder.main.mixins import AutocompletePerformanceMixin

from .models import Monitoring


class MonitoringAutocomplete(AutocompletePerformanceMixin,
                             autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    select_only = ['id', 'name']
autocomplete_light.register(Monitoring, MonitoringAutocomplete)
