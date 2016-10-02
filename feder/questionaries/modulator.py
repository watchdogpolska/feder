from __future__ import unicode_literals

import shlex

from dal import autocomplete
from django import forms
from django.utils.translation import ugettext_lazy as _

from feder.teryt.models import JST

SHLEX_TEXT = _("Enter as space-seperated text. Use quotes to pass sentences.")

modulators = {}


def register(name):
    def decorator(cls):
        modulators[name] = cls
        return cls
    return decorator


class BaseModulator(object):

    @classmethod
    @property
    def description(self):
        raise NotImplementedError("Provide property 'description' in {name}".
                                  format(name=self.__class__.__name__))

    def list_create_question_fields(self):
        raise NotImplementedError("Provide method 'list_create_question_fields' in {name}".
                                  format(name=self.__class__.__name__))

    def list_create_answer_fields(self, definition):
        raise NotImplementedError("Provide method 'list_create_answer_fields' in {name}".
                                  format(name=self.__class__.__name__))

    def get_content(self, definition, cleaned_data):
        return cleaned_data

    def get_label_text(self, definition):
        raise NotImplementedError("Provide method 'get_label_text' in {name}".
                                  format(name=self.__class__.__name__))

    def get_answer_text(self, definition, content):
        raise NotImplementedError("Provide method 'get_answer_text' in {name}".
                                  format(name=self.__class__.__name__))

    def get_initial(self, definition, content):
        return content

    def get_label_column(self, definition):
        raise NotImplementedError("Provide method 'get_label_column' in {name}".
                                  format(name=self.__class__.__name__))

    def get_answer_columns(self, definition, content):
        raise NotImplementedError("Provide method 'get_answer_columns' in {name}".
                                  format(name=self.__class__.__name__))


class BaseSimpleModulator(BaseModulator):
    output_field_cls = None

    def list_create_question_fields(self):
        return (('name', forms.CharField(label=_("Question"))),
                ('help_text', forms.CharField(label=_("Description of question"))),
                ('required', forms.BooleanField(label=_("This fields will be required?"),
                                                required=False)),
                ('comment', forms.BooleanField(label=_("Allow comment"),
                                               required=False)),
                ('comment_label', forms.CharField(label=_("Description of comment"),
                                                  required=False)),
                ('comment_help', forms.CharField(label=_("Help text of comment"),
                                                 required=False)),
                ('comment_required', forms.BooleanField(label=_("Are comment required?"),
                                                        required=False)))

    def get_kwargs(cls, definition):
        return dict(label=definition.get('name', ""),
                    help_text=definition.get('help_text', ""),
                    required=definition.get('required', True))

    def list_create_answer_fields(cls, definition):
        definition = definition or {}
        fields = [('value', cls.output_field_cls(**cls.get_kwargs(definition))), ]
        if definition.get('comment', True):
            commend_field = forms.CharField(label=definition.get('comment_label', ""),
                                            help_text=definition.get('comment_help', ""),
                                            required=not definition.get('comment_required', False))
            fields.append(('comment', commend_field), )
        return fields

    def get_label_text(cls, definition):
        definition = definition or {}
        return definition.get('name', '')

    def get_answer_text(cls, definition, content):
        definition = definition or {}
        if definition.get('comment', False):
            return u"%s (%s)" % (content.get('value', ''), content.get('comment', ''))
        return content.get('value', '')

    def get_label_column(cls, definition):
        definition = definition or {}
        return [definition.get('name', ''), "Comment"]

    def get_answer_columns(cls, definition, content):
        return [content['value'], content['comment']]


@register('char')
class CharModulator(BaseSimpleModulator):
    description = _("Question about char")
    output_field_cls = forms.CharField


@register('int')
class IntegerModulator(BaseSimpleModulator):
    description = _("Question about integer")
    output_field_cls = forms.CharField


@register('email')
class EmailModulator(BaseSimpleModulator):
    description = _("Question about e-mail")
    output_field_cls = forms.CharField


@register('date')
class DateModulator(BaseSimpleModulator):
    description = _("Question about date")
    output_field_cls = forms.DateField


@register('choice')
class ChoiceModulator(BaseSimpleModulator):
    description = _("Question to choices")
    output_field_cls = forms.ChoiceField

    def list_create_question_fields(self, fields):
        items = super(ChoiceModulator, self).create(fields)
        choices_field = forms.CharField(label=_("Choices"),
                                        help_text=SHLEX_TEXT)
        items += ('choices', choices_field)
        return items

    def get_kwargs(self, definition):
        kw = super(ChoiceModulator, self).get_kwargs(definition)
        kw['choices'] = enumerate(shlex.split(definition['choices'].encode('utf-8')))
        return kw

    def get_label_text(self, definition):
        return definition['name']

    def get_answer_columns(self, definition):
        choices = shlex.split(definition['choices'].encode('utf-8'))
        v = choices[int(definition['value'])]
        if definition:
            return [v, definition['comment']]
        if definition['comment']:
            return "%s (%s)" % (v, definition['comment'])
        return v


@register('jst')
class JSTModulator(BaseSimpleModulator):
    description = _("Question about unit of administrative division")
    output_fields_cls = forms.ModelChoiceField
    CHOICES = {'voivodeship': _("Voivodeship"),
               'community': _("Community"),
               'county': _("County"),
               'all': _("All")}

    def list_create_question_fields(self):
        return (('name', forms.CharField(label=_("Question"))),
                ('help_text', forms.CharField(label=_("Description of question"))),
                ('required', forms.BooleanField(label=_("This fields will be required?"),
                                                required=False)),
                ('area', forms.ChoiceField(choices=self.CHOICES.items(),
                                           label=("Area"))),
                ('autocomplete', forms.BooleanField(label=_("Display as autocomplete?"),
                                                    required=False))
                )

    def list_create_answer_fields(self, definition):
        definition.setdefault('name', '')
        definition.setdefault('help_text', '')
        definition.setdefault('area', 'voivodeship')
        definition.setdefault('required', True)
        kwargs = {}
        kwargs['label'] = definition['name']
        kwargs['help_text'] = definition['help_text']
        kwargs['required'] = definition['required']

        if definition['area'] == 'voivodeship':
            # kwargs['widget'] = autocomplete.ModelSelect2(
            #         url='teryt:voivodeship-autocomplete')
            kwargs['queryset'] = JST.objects.voivodeship().all()
        elif definition['area'] == 'community':
            # kwargs['widget'] = autocomplete.ModelSelect2(
            #         url='teryt:community-autocomplete')
            kwargs['queryset'] = JST.objects.community().all()
        elif definition['area'] == 'county':
            # kwargs['widget'] = autocomplete.ModelSelect2(
            #         url='teryt:county-autocomplete')
            kwargs['queryset'] = JST.objects.county().all()
        else:
            kwargs['queryset'] = JST.objects.all()
        return (('value', forms.ModelChoiceField(**kwargs)),
                )

    def get_content(self, definition, content):
        if isinstance(content['value'], JST):
            content['value'] = content['value'].pk
        return content

    def get_label_text(self, definition):
        return definition['name']

    def get_answer_text(self, definition, content):
        return JST.objects.get(pk=content['value'])

    def get_initial(self, definition, content):
        return content
        return {'value': JST.objects.get(pk=content['value']).pk}

    def get_label_column(self, definition):
        return [definition['name'], "JST-id"]

    def get_answer_columns(self, definition, content):
        return [JST.objects.get(pk=content['value']), content['value']]
