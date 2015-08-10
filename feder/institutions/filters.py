from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext as _
from crispy_forms.layout import Submit
import django_filters
import autocomplete_light
from feder.teryt.filters import JSTModelChoice
from .models import Institution, Tag


class InstitutionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    voivodeship = JSTModelChoice(level=1, label=_("Vovivodeship"))
    county = JSTModelChoice(level=2, label=_("County"))
    community = JSTModelChoice(level=3, label=_("Community"))
    tags = django_filters.ModelChoiceFilter(queryset=Tag.objects.all(),
        widget=autocomplete_light.ChoiceWidget('TagAutocomplete'))

    def __init__(self, *args, **kwargs):
        super(InstitutionFilter, self).__init__(*args, **kwargs)
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
