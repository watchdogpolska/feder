import autocomplete_light
from models import Monitoring

# This will generate a MonitoringAutocomplete class
autocomplete_light.register(Monitoring,
    # Just like in ModelAdmin.search_fields
    search_fields=['name'],
)
