import autocomplete_light
from .models import Monitoring


class MonitoringAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choices_for_request(self, *args, **kwargs):
        qs = super(MonitoringAutocomplete, self).choices_for_request(*args, **kwargs)
        return qs.only('id', 'name')
autocomplete_light.register(Monitoring, MonitoringAutocomplete)
