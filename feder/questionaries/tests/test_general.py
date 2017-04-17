from feder.users.factories import UserFactory

from ..factories import QuestionaryFactory


class ObjectMixin(object):
    def setUp(self):
        self.user = UserFactory(username='john', )
        self.questionary = QuestionaryFactory()
        self.permission_object = self.questionary.monitoring
