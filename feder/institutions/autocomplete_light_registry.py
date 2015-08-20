import autocomplete_light
from models import Institution, Tag


class InstitutionAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choices_for_request(self, *args, **kwargs):
        qs = super(InstitutionAutocomplete, self).choices_for_request(*args, **kwargs)
        return qs.only('id', 'name')
autocomplete_light.register(Institution, InstitutionAutocomplete)


class TagAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choices_for_request(self, *args, **kwargs):
        qs = super(TagAutocomplete, self).choices_for_request(*args, **kwargs)
        return qs.only('id', 'name')
autocomplete_light.register(Tag, TagAutocomplete)
