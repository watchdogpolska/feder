import autocomplete_light
from .models import Institution, Tag
from feder.main.mixins import AutocompletePerformanceMixin


class InstitutionAutocomplete(AutocompletePerformanceMixin,
        autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    select_only = ['id', 'name']
autocomplete_light.register(Institution, InstitutionAutocomplete)


class TagAutocomplete(AutocompletePerformanceMixin, autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
autocomplete_light.register(Tag, TagAutocomplete)
