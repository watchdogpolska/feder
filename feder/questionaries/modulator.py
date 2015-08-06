from django import forms
from django.utils.translation import ugettext as _


class BaseBlobFormModulator(object):
    description = None

    def __init__(self, blob=None):
        self.blob = blob or {}
        super(BaseBlobFormModulator, self).__init__()

    def create(self, fields):
        raise NotImplementedError("Provide method 'create'")

    def answer(self, fields):
        raise NotImplementedError("Provide method 'answer'")

    def read(self, cleaned_data):
        raise NotImplementedError("Provide method 'read'")


class BaseSimpleModulator(BaseBlobFormModulator):
    output_field_cls = None

    def create(self, fields):
        fields['name'] = forms.CharField(label=_("Question"))
        fields['help_text'] = forms.CharField(label=_("Description of question"))
        fields['required'] = forms.BooleanField(label=_("This fields is required?"))

    def answer(self, fields):
        fields['value'] = self.output_field_cls(label=self.blob['name'],
            help_text=self.blob['help_text'], required=self.blob.get('required', True))

    def read(self, cleaned_data):
        return cleaned_data['value']


class CharModulator(BaseSimpleModulator):
    description = "Char modulator"
    output_field_cls = forms.CharField


class IntegerModulator(BaseSimpleModulator):
    description = "Integer modulator"
    output_field_cls = forms.CharField


class EmailModulator(BaseSimpleModulator):
    description = "E-mail modulator"
    output_field_cls = forms.CharField

modulators = {'char': CharModulator,
              'int': IntegerModulator,
              'email': EmailModulator}
