import autocomplete_light
from models import Questionary

# This will generate a MonitoringAutocomplete class
autocomplete_light.register(Questionary,
    # Just like in ModelAdmin.search_fields
    search_fields=['title'],
)
