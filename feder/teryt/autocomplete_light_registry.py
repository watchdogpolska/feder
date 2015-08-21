import autocomplete_light
from .models import JednostkaAdministracyjna

# This will generate a PersonAutocomplete class
autocomplete_light.register(JednostkaAdministracyjna,
    # Just like in ModelAdmin.search_fields
    search_fields=['name'],
)
