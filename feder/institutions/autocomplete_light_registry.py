import autocomplete_light
from .models import JST


# class JSTAutocompleteMixin(autocomplete_light.AutocompleteModelBase):
class JSTAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['nazwa']
    model = JST

    def choices_for_request(self):
        if 'parent' in self.request.GET:
            self.choices = self.choices.filter(id__startswith=self.request.GET.get('parent'))
        return super(JSTAutocomplete, self).choices_for_request()
autocomplete_light.register(JST, JSTAutocomplete)


class VoivodeshipAutocomplete(JSTAutocomplete):
    def choices_for_request(self):
        self.choices = self.choices.wojewodztwa()
        return super(VoivodeshipAutocomplete, self).choices_for_request()

autocomplete_light.register(JST, VoivodeshipAutocomplete)


class CountyAutocomplete(JSTAutocomplete):
    def choices_for_request(self):
        self.choices = self.choices.powiaty()
        return super(CountyAutocomplete, self).choices_for_request()

autocomplete_light.register(JST, CountyAutocomplete)


class CommunityAutocomplete(JSTAutocomplete):
    def choices_for_request(self):
        self.choices = self.choices.gminy()
        return super(CommunityAutocomplete, self).choices_for_request()
autocomplete_light.register(JST, CommunityAutocomplete)
