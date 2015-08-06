import autocomplete_light
from models import Case

autocomplete_light.register(Case,
    search_fields=['name'],
)
