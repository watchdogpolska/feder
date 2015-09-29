from __future__ import unicode_literals

import shlex

from django import forms
from django.utils.translation import ugettext_lazy as _

SHLEX_TEXT = _("Enter as space-seperated text. Use quotes to pass sentences.")


class BaseBlobFormModulator(object):
    description = None

    def __init__(self, blob=None):
        self.blob = blob if blob else {}
        super(BaseBlobFormModulator, self).__init__()

    def create(self, fields):
        """ Method to add fields to create question form"""
        raise NotImplementedError("Provide method 'create' in {name}".
                                  format(name=self.__class__.__name__))

    def answer(self, fields):
        """ Method to add fields to answer form """
        raise NotImplementedError("Provide method 'answer' in {name}".
                                  format(name=self.__class__.__name__))

    def read(self, cleaned_data):
        """ Method to convert answer for dict for store """
        raise NotImplementedError("Provide method 'read' in {name}".
                                  format(name=self.__class__.__name__))

    def render_label(self, sheet=False):
        """ Method to convert question to user-friendly label"""
        raise NotImplementedError("Provide method 'read' in {name}".
                                  format(name=self.__class__.__name__))

    def render_answer(self, blob, sheet=False):
        """ Method to convert answer to user-friendly text"""
        raise NotImplementedError("Provide method 'read' in {name}".
                                  format(name=self.__class__.__name__))


class BaseSimpleModulator(BaseBlobFormModulator):
    output_field_cls = None

    def create(self, fields):
        fields['name'] = forms.CharField(label=_("Question"))
        fields['help_text'] = forms.CharField(label=_("Description of question"))
        fields['required'] = forms.BooleanField(label=_("This fields will be required?"),
                                                required=False)
        fields['comment'] = forms.BooleanField(label=_("Allow comment"),
                                               required=False)
        fields['comment_label'] = forms.CharField(label=_("Description of comment"),
                                                  required=False)
        fields['comment_help'] = forms.CharField(label=_("Help text of comment"),
                                                 required=False)
        fields['comment_required'] = forms.BooleanField(label=_("Are comment required?"),
                                                        required=False)

    def get_kwargs(self):
        return dict(label=self.blob['name'],
                    help_text=self.blob['help_text'],
                    required=self.blob.get('required', True))

    def answer(self, fields):
        fields['value'] = self.output_field_cls(**self.get_kwargs())
        if self.blob.get('comment', True):
            fields['comment'] = forms.CharField(label=self.blob['comment_label'],
                                                help_text=self.blob['comment_help'],
                                                required=not self.blob['comment_required'])

    def read(self, cleaned_data):
        return {'value': cleaned_data['value'], 'comment': cleaned_data['value']}

    def render_label(self, sheet=False):
        if sheet:
            return [self.blob['name'], 'Comment']
        return self.blob['name']

    def render_answer(self, blob, sheet=False):
        if sheet:
            return [blob['value'], blob['comment']]
        if blob['comment']:
            return "%s (%s)" % (blob['value'], blob['comment'])
        return blob['value']


class CharModulator(BaseSimpleModulator):
    description = _("Question about char")
    output_field_cls = forms.CharField


class IntegerModulator(BaseSimpleModulator):
    description = _("Question about integer")
    output_field_cls = forms.CharField


class EmailModulator(BaseSimpleModulator):
    description = _("Question about e-mail")
    output_field_cls = forms.CharField


class DateModulator(BaseSimpleModulator):
    description = _("Question about date")
    output_field_cls = forms.DateField


class ChoiceModulator(BaseSimpleModulator):
    description = _("Question to choices")
    output_field_cls = forms.ChoiceField

    def create(self, fields):
        super(ChoiceModulator, self).create(fields)
        fields['choices'] = forms.CharField(label=_("Choices"),
                                            help_text=SHLEX_TEXT)

    def get_kwargs(self, *args, **kwargs):
        kw = super(ChoiceModulator, self).get_kwargs(*args, **kwargs)
        kw['choices'] = enumerate(shlex.split(self.blob['choices'].encode('utf-8')))
        return kw

    def render_answer(self, blob, sheet=False):
        choices = shlex.split(self.blob['choices'].encode('utf-8'))
        v = choices[int(blob['value'])]
        if sheet:
            return [v, blob['comment']]
        if blob['comment']:
            return "%s (%s)" % (v, blob['comment'])
        return v


class JSTModulator(BaseSimpleModulator):
    description = _("Question about unit of administrative division")

    def answer(self, fields):
        import autocomplete_light
        fields['value'] = autocomplete_light.ModelMultipleChoiceField(
            'JednostkaAdministracyjnaAutocomplete',
            label=self.blob['name'],
            help_text=self.blob['help_text'],
            required=self.blob.get('required', True))

modulators = {'char': CharModulator,
              'int': IntegerModulator,
              'email': EmailModulator,
              'jst': JSTModulator,
              'date': DateModulator,
              'choice': ChoiceModulator}
