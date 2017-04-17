import factory

from feder.monitorings.factories import MonitoringFactory
from .models import Questionary, Question


class QuestionaryFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence('questionary-{0}'.format)
    monitoring = factory.SubFactory(MonitoringFactory)

    class Meta:
        model = Questionary


class CharQuestionFactory(factory.django.DjangoModelFactory):
    questionary = factory.SubFactory(QuestionaryFactory)
    position = factory.Sequence(lambda x: x)
    genre = 'char'

    class Params:
        comment = None
        comment_help = None
        comment_label = None
        comment_required = None
        help_text = None
        name = None

    @factory.lazy_attribute_sequence
    def definition(self, n):
        default = {u'comment': n % 2 == 0,
                   u'comment_help': 'Standard help text no. {0}'.format(n),
                   u'comment_label': u'Standard comment label {0}'.format(n),
                   u'comment_required': n % 2 == 0,
                   u'help_text': u'Answer me, please!',
                   u'name': u'Question no.{0} ?'.format(n)}
        result = {}
        for key, value in default.items():
            result[key] = value if getattr(self, key) is None else getattr(self, key)
        return result

    class Meta:
        model = Question


class JSTQuestionFactory(factory.django.DjangoModelFactory):
    questionary = factory.SubFactory(QuestionaryFactory)
    position = factory.Sequence(lambda x: x)
    genre = 'jst'

    class Params:
        name = None
        help_text = None
        required = None
        area = 'all'
        autocomplete = None

    @factory.lazy_attribute_sequence
    def definition(self, n):
        default = {u'name': 'Standard name no. {0}'.format(n),
                   u'help_text': 'Standard help text no. {0}'.format(n),
                   u'required': n % 2 == 0,
                   u'area': 'all'}
        result = {}
        for key, value in default.items():
            result[key] = value if getattr(self, key) is None else getattr(self, key)
        return result

    class Meta:
        model = Question
