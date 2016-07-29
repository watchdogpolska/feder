from autocomplete_light import shortcuts as autocomplete_light

from feder.main.mixins import AutocompletePerformanceMixin

from .models import Case


class CaseAutocomplete(AutocompletePerformanceMixin, autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    select_only = ['id', 'name']
autocomplete_light.register(Case, CaseAutocomplete)
