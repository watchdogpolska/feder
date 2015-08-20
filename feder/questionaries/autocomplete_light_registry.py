import autocomplete_light
from models import Questionary


class QuestionaryAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['title']

    def choices_for_request(self, *args, **kwargs):
        qs = super(QuestionaryAutocomplete, self).choices_for_request(*args, **kwargs)
        return qs.only('id', 'title')
autocomplete_light.register(Questionary, QuestionaryAutocomplete)
