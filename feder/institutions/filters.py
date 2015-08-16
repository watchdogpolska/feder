from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Submit
import django_filters
from feder.teryt.filters import JSTModelChoice
from atom.filters import AutocompleteChoiceFilter
from .models import Institution


class InstitutionFilter(django_filters.FilterSet):
    voivodeship = JSTModelChoice(level=1, label=_("Voivodeship"))
    county = JSTModelChoice(level=2, label=_("County"))
    community = JSTModelChoice(level=3, label=_("Community"))
    tags = AutocompleteChoiceFilter('TagAutocomplete', label=_("Tags"))

    def __init__(self, *args, **kwargs):
        super(InstitutionFilter, self).__init__(*args, **kwargs)
        self.filters['name'].lookup_type = 'icontains'
        if self.data.get('voivodeship', None):
            self.filters['county'].limit_parent(self.data.get('voivodeship'))
            if self.data.get('county', None):
                self.filters['community'].limit_parent(self.data.get('county'))
            else:
                del self.filters['community']
        else:
            del self.filters['county']
            del self.filters['community']

    @property
    def form(self):
        self._form = super(InstitutionFilter, self).form
        self._form.helper = FormHelper(self._form)
        # self._form.helper.form_class = 'form-inline'
        self._form.helper.form_method = 'get'
        self._form.helper.layout.append(Submit('filter', _('Filter')))
        return self._form

    class Meta:
        model = Institution
        fields = ['name', 'tags']
        order_by = ['-case_count', 'jst']
