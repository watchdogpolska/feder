import factory

from feder.monitorings.factories import MonitoringFactory
from .models import Questionary, Question


class QuestionaryFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence("questionary-{}".format)
    monitoring = factory.SubFactory(MonitoringFactory)

    class Meta:
        model = Questionary


class CharQuestionFactory(factory.django.DjangoModelFactory):
    questionary = factory.SubFactory(QuestionaryFactory)
    position = factory.Sequence(lambda x: x)
    genre = "char"

    class Params:
        comment = None
        comment_help = None
        comment_label = None
        comment_required = None
        help_text = None
        name = None

    @factory.lazy_attribute_sequence
    def definition(self, n):
        default = {
            "comment": n % 2 == 0,
            "comment_help": "Standard help text no. {}".format(n),
            "comment_label": "Standard comment label {}".format(n),
            "comment_required": n % 2 == 0,
            "help_text": "Answer me, please!",
            "name": "Question no.{} ?".format(n),
        }
        result = {}
        for key, value in default.items():
            result[key] = value if getattr(self, key) is None else getattr(self, key)
        return result

    class Meta:
        model = Question


class JSTQuestionFactory(factory.django.DjangoModelFactory):
    questionary = factory.SubFactory(QuestionaryFactory)
    position = factory.Sequence(lambda x: x)
    genre = "jst"

    class Params:
        name = None
        help_text = None
        required = None
        area = "all"
        autocomplete = None

    @factory.lazy_attribute_sequence
    def definition(self, n):
        default = {
            "name": "Standard name no. {}".format(n),
            "help_text": "Standard help text no. {}".format(n),
            "required": n % 2 == 0,
            "area": "all",
        }
        result = {}
        for key, value in default.items():
            result[key] = value if getattr(self, key) is None else getattr(self, key)
        return result

    class Meta:
        model = Question
