from django.views.generic import DetailView
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext as _
from crispy_forms.layout import Submit
import django_filters
from .models import Institution


class InstitutionFilter(django_filters.FilterSet):
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
        fields = ['tags']


class InstitutionListView(FilterView):
    filterset_class = InstitutionFilter
    model = Institution


class InstitutionDetailView(DetailView):
    model = Institution
