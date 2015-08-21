import autocomplete_light
from feder.main.mixins import AutocompletePerformanceMixin

from .models import Questionary


class QuestionaryAutocomplete(AutocompletePerformanceMixin,
        autocomplete_light.AutocompleteModelBase):
    search_fields = ['title']
    select_only = ['id', 'title']
autocomplete_light.register(Questionary, QuestionaryAutocomplete)
