import factory

from .models import Task, Survey
from feder.questionaries.factories import QuestionaryFactory
from feder.cases.factories import CaseFactory


class TaskFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('task-{0}'.format)
    case = factory.SubFactory(CaseFactory)
    questionary = factory.SubFactory(QuestionaryFactory)

    class Meta:
        model = Task


class SurveyFactory(factory.django.DjangoModelFactory):
    task = factory.SubFactory(Task)

    class Meta:
        model = Survey
