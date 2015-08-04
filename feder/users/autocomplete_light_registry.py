import autocomplete_light
from models import User

# This will generate a PersonAutocomplete class
autocomplete_light.register(User,
    # Just like in ModelAdmin.search_fields
    search_fields=['username'],
)
