from __future__ import unicode_literals

import shlex
from collections import OrderedDict

from dal import autocomplete
from django import forms
from django.utils.translation import ugettext_lazy as _

from feder.letters.models import Letter
from feder.teryt.models import JST

SHLEX_TEXT = _("Enter as space-seperated text. Use quotes to pass sentences.")


class BaseModulator(object):
    """Abstract modulator which define interface
    """
    @classmethod
    @property
    def description(self):
        """A description of modulator visible for user"""
        raise NotImplementedError("Provide property 'description' in {name}".
                                  format(name=self.__class__.__name__))

    def list_create_question_fields(self):
        """A list of fields to create question defintion

        Returns:
            list of tuple (field name, field): List of fields

        """
        raise NotImplementedError("Provide method 'list_create_question_fields' in {name}".
                                  format(name=self.__class__.__name__))

    def list_create_answer_fields(self, definition, survey=None):
        """A list to fields to create answer (review in case)

        Args:
            definition (dict): A question definition
            survey (None, optional): A survey object

        Returns:
            list of tuple (field name, field): Description
        """
        raise NotImplementedError("Provide method 'list_create_answer_fields' in {name}".
                                  format(name=self.__class__.__name__))

    def get_content(self, definition, cleaned_data):
        """Returns content of answer

        Args:
            definition (dict): Definition of question
            cleaned_data (dict): Cleaned data of answer

        Returns:
            str: Content of answer
        """
        return cleaned_data

    def get_label_text(self, definition):
        """Returns label of question

        Args:
            definition (dict): Definition of question

        Returns:
            str: Label of question
        """
        raise NotImplementedError("Provide method 'get_label_text' in {name}".
                                  format(name=self.__class__.__name__))

    def get_answer_text(self, definition, content):
        """Returns answer of text for simple preview

        Args:
            definition (dict): Definition of question
            content (TYPE): Description

        Returns:
            TYPE: Description
        """
        raise NotImplementedError("Provide method 'get_answer_text' in {name}".
                                  format(name=self.__class__.__name__))

    def get_initial(self, definition, content):
        """Returns initial values of submit forms

        Args:
            definition (dict): Definition of question
            content (dict): Data content of answer
        """
        return content

    def get_label_column(self, definition):
        """Returns labels of columns to CSV export

        Args:
            definition (dict): Definition of question
        """
        raise NotImplementedError("Provide method 'get_label_column' in {name}".
                                  format(name=self.__class__.__name__))

    def get_answer_columns(self, definition, content):
        """Returns values of columns to CSV export

        Args:
            definition (dict): Definition of question
            content (dict): Content of question
        """
        raise NotImplementedError("Provide method 'get_answer_columns' in {name}".
                                  format(name=self.__class__.__name__))


class BaseSimpleModulator(BaseModulator):
    """A standard implementation to simple modulator

    Attributes:
        output_field_cls (django.form.fields): A class used to widget in submit form
    """
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

    def get_kwargs(self, definition):
        return dict(label=definition.get('name', ""),
                    help_text=definition.get('help_text', ""),
                    required=definition.get('required', True))

    def list_create_answer_fields(self, definition, survey=None):
        definition = definition or {}
        fields = [('value', self.output_field_cls(**self.get_kwargs(definition))), ]
        if definition.get('comment', True):
            commend_field = forms.CharField(label=definition.get('comment_label', ""),
                                            help_text=definition.get('comment_help', ""),
                                            required=not definition.get('comment_required', False))
            fields.append(('comment', commend_field), )
        return fields

    def get_label_text(self, definition):
        definition = definition or {}
        return definition.get('name', '')

    def get_answer_text(self, definition, content):
        definition = definition or {}
        if definition.get('comment', False):
            return u"%s (%s)" % (content.get('value', ''), content.get('comment', ''))
        return content.get('value', '')

    def get_label_column(self, definition):
        definition = definition or {}
        return [definition.get('name', ''), "Comment"]

    def get_answer_columns(self, definition, content):
        return [content['value'], content.get('comment', '')]


class CharModulator(BaseSimpleModulator):
    name = 'char'
    description = _("Question about char")
    output_field_cls = forms.CharField


class IntegerModulator(BaseSimpleModulator):
    name = 'int'
    description = _("Question about integer")
    output_field_cls = forms.CharField


class EmailModulator(BaseSimpleModulator):
    name = 'email'
    description = _("Question about e-mail")
    output_field_cls = forms.CharField


class DateModulator(BaseSimpleModulator):
    name = 'date'
    description = _("Question about date")
    output_field_cls = forms.DateField


class ChoiceModulator(BaseSimpleModulator):
    name = 'choice'
    description = _("Question to choices")
    output_field_cls = forms.ChoiceField

    def list_create_question_fields(self):
        items = super(ChoiceModulator, self).list_create_question_fields()
        choices_field = forms.CharField(label=_("Choices"),
                                        help_text=SHLEX_TEXT)
        items += (('choices', choices_field), )
        return items

    def get_kwargs(self, definition):
        kw = super(ChoiceModulator, self).get_kwargs(definition)
        kw['choices'] = enumerate(shlex.split(definition['choices'].encode('utf-8')))
        return kw

    def get_label_text(self, definition):
        return definition['name']

    def get_answer_columns(self, definition, content):
        choices = shlex.split(definition['choices'].encode('utf-8'))
        v = choices[int(content['value'])]
        if definition:
            return [v, definition['comment']]
        if definition['comment']:
            return "%s (%s)" % (v, definition['comment'])
        return v


class JSTModulator(BaseSimpleModulator):
    """Summary

    Attributes:
        CHOICES (dict): Labels of choices of type of division
        description (str): Description of question
        output_field_cls (django.form.fields): A class used to widget in submit form
    """
    name = 'jst'
    description = _("Question about unit of administrative division")
    output_fields_cls = forms.ModelChoiceField
    CHOICES = OrderedDict([('voivodeship', _("Voivodeship")),
                           ('community', _("Community")),
                           ('county', _("County")),
                           ('all', _("All"))
                           ])

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

    def list_create_answer_fields(self, definition, survey=None):
        definition.setdefault('name', '')
        definition.setdefault('help_text', '')
        definition.setdefault('area', 'voivodeship')
        definition.setdefault('required', True)
        kwargs = {}
        kwargs['label'] = definition['name']
        kwargs['help_text'] = definition['help_text']
        kwargs['required'] = definition['required']

        if definition['area'] == 'voivodeship':
            kwargs['widget'] = autocomplete.ModelSelect2(
                url='teryt:voivodeship-autocomplete')
            kwargs['queryset'] = JST.objects.voivodeship().all()
        elif definition['area'] == 'community':
            kwargs['widget'] = autocomplete.ModelSelect2(
                url='teryt:community-autocomplete')
            kwargs['queryset'] = JST.objects.community().all()
        elif definition['area'] == 'county':
            kwargs['widget'] = autocomplete.ModelSelect2(
                url='teryt:county-autocomplete')
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


class LetterChoiceModulator(BaseSimpleModulator):
    """Summary

    Attributes:
        CHOICES (TYPE): Description
        description (TYPE): Description
        output_fields_cls (TYPE): Description
    """
    name = 'letter'
    description = _("Question about letter of case")
    output_fields_cls = forms.ModelChoiceField
    CHOICES = {'all': _("All"),
               'outgoing': _("Outgoing"),
               'incoming': _("Incoming")}

    def list_create_question_fields(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return (('name', forms.CharField(label=_("Question"))),
                ('help_text', forms.CharField(label=_("Description of question"))),
                ('required', forms.BooleanField(label=_("This fields will be required?"),
                                                required=False)),
                ('filter', forms.ChoiceField(choices=self.CHOICES.items(),
                                             label=("Filter"),
                                             help_text=_("Specifiy which letter "
                                                         "user should be able to select")))
                )

    def choice_map(self, queryset, choice):
        """Summary

        Args:
            queryset (TYPE): Description
            choice (TYPE): Description

        Returns:
            TYPE: Description
        """
        mapping = {'all': lambda x: x,
                   'outgoing': lambda x: x.is_outgoing(),
                   'incoming': lambda x: x.is_incoming()}
        return mapping[choice](queryset)

    def list_create_answer_fields(self, definition, survey=None):
        """Summary

        Args:
            definition (TYPE): Description
            survey (None, optional): Description

        Returns:
            TYPE: Description
        """
        definition.setdefault('name', '')
        definition.setdefault('help_text', '')
        definition.setdefault('required', True)
        definition.setdefault('filter', 'all')
        kwargs = {}
        kwargs['label'] = definition['name']
        kwargs['help_text'] = definition['help_text']
        kwargs['required'] = definition['required']
        if survey is None:
            kwargs['queryset'] = Letter.objects.none()
        else:
            kwargs['queryset'] = self.choice_map(survey.case.letter_set.all(), definition['filter'])
        return (('value', forms.ModelChoiceField(**kwargs)), )

    def get_content(self, definition, content):
        """Summary

        Args:
            definition (TYPE): Description
            content (TYPE): Description

        Returns:
            TYPE: Description
        """
        if isinstance(content['value'], Letter):
            content['value'] = content['value'].pk
        return content

    def get_label_text(self, definition):
        """Summary

        Args:
            definition (TYPE): Description

        Returns:
            TYPE: Description
        """
        return definition['name']

    def get_answer_text(self, definition, content):
        """Summary

        Args:
            definition (TYPE): Description
            content (TYPE): Description

        Returns:
            TYPE: Description
        """
        try:
            return Letter.objects.get(pk=content['value'])
        except Letter.DoesNotExist:
            return "#N/N"

    def get_initial(self, definition, content):
        """Summary

        Args:
            definition (TYPE): Description
            content (TYPE): Description

        Returns:
            TYPE: Description
        """
        return content

    def get_label_column(self, definition):
        """Summary

        Args:
            definition (TYPE): Description

        Returns:
            TYPE: Description
        """
        return ["%s-%s" % (definition['name'], 'post-id'),
                "%s-%s" % (definition['name'], 'post-date')]

    def get_answer_columns(self, definition, content):
        """Summary

        Args:
            definition (TYPE): Description
            content (TYPE): Description

        Returns:
            TYPE: Description
        """
        return [self.get_answer_text(definition, content), content['value']]
