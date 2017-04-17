import factory

from feder.cases.factories import CaseFactory
from feder.questionaries.factories import (CharQuestionFactory,
                                           JSTQuestionFactory,
                                           QuestionaryFactory)
from feder.teryt.factories import JSTFactory
from feder.users.factories import UserFactory
from .models import Answer, Survey, Task


class TaskFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('task-{0}'.format)
    case = factory.SubFactory(CaseFactory)
    questionary = factory.SubFactory(QuestionaryFactory)

    class Meta:
        model = Task


class SurveyFactory(factory.django.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Survey


class CharAnswerFactory(factory.django.DjangoModelFactory):
    question = factory.SubFactory(CharQuestionFactory,
                                  questionary=factory.SelfAttribute('..survey.task.questionary'))
    survey = factory.SubFactory(SurveyFactory)

    @factory.lazy_attribute_sequence
    def content(self, n):
        return {u'comment': u'comment-{0}'.format(n),
                u'value': u'foo-uniq-{0}'.format(n)}

    class Meta:
        model = Answer


class JSTAnswerFactory(factory.django.DjangoModelFactory):
    question = factory.SubFactory(JSTQuestionFactory,
                                  questionary=factory.SelfAttribute('..survey.task.questionary'))
    survey = factory.SubFactory(SurveyFactory)

    class Params:
        comment = None
        value = None

    @factory.lazy_attribute_sequence
    def content(self, n):
        default = {u'comment': u'comment-{0}'.format(n),
                   u'value': JSTFactory().pk}
        result = {}
        for key, value in default.items():
            result[key] = value if getattr(self, key) is None else getattr(self, key)
        return result

    class Meta:
        model = Answer
