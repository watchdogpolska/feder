from __future__ import unicode_literals
import autocomplete_light

from .models import JednostkaAdministracyjna

from django.utils.encoding import force_text


class JednostkaAdministracyjnaAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
autocomplete_light.register(JednostkaAdministracyjna, JednostkaAdministracyjnaAutocomplete)


class CommunityAutocomplete(JednostkaAdministracyjnaAutocomplete):
    def choice_label(self, choice):
        return "{parent} > {choice}".format(parent=force_text(choice.parent),
                                            choice=force_text(choice))

    def choices_for_request(self):
        self.choices = self.choices.filter(category__level=3).select_related('parent')
        return super(CommunityAutocomplete, self).choices_for_request()

autocomplete_light.register(JednostkaAdministracyjna, CommunityAutocomplete)
