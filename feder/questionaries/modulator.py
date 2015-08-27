from django import forms
from django.utils.translation import ugettext_lazy as _


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
        fields['required'] = forms.BooleanField(label=_("This fields will be required?"),
                                                required=False)

    def answer(self, fields):
        fields['value'] = self.output_field_cls(label=self.blob['name'],
                                                help_text=self.blob['help_text'], required=self.blob.get('required', True))

    def read(self, cleaned_data):
        return cleaned_data['value']

    def render_answer(self, blob):
        return blob

    def render_label(self):
        return self.blob['name']


class CharModulator(BaseSimpleModulator):
    description = _("Question about char")
    output_field_cls = forms.CharField


class IntegerModulator(BaseSimpleModulator):
    description = _("Question about integer")
    output_field_cls = forms.CharField


class EmailModulator(BaseSimpleModulator):
    description = _("Question about e-mail")
    output_field_cls = forms.CharField


class JSTModulator(BaseSimpleModulator):
    description = _("Question about unit of administrative division")

    def answer(self, fields):
        import autocomplete_light
        fields['value'] = autocomplete_light.ModelMultipleChoiceField(
            'JednostkaAdministracyjnaAutocomplete', label=self.blob['name'],
            help_text=self.blob['help_text'],
            required=self.blob.get('required', True))

modulators = {'char': CharModulator,
              'int': IntegerModulator,
              'email': EmailModulator,
              'jst': JSTModulator}
