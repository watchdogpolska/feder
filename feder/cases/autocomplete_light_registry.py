import autocomplete_light
from models import Case


class CaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choices_for_request(self, *args, **kwargs):
        qs = super(CaseAutocomplete, self).choices_for_request(*args, **kwargs)
        return qs.only('id', 'name')
autocomplete_light.register(Case, CaseAutocomplete)
