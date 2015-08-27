import autocomplete_light

from .models import User


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['username']

    def choices_for_request(self, *args, **kwargs):
        qs = super(UserAutocomplete, self).choices_for_request(*args, **kwargs)
        return qs.only('username')
autocomplete_light.register(User, UserAutocomplete)
