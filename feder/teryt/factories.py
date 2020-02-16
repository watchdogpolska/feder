import factory
from teryt_tree.factories import JednostkaAdministracyjnaFactory

from feder.teryt.models import JST


class JSTFactory(JednostkaAdministracyjnaFactory):
    class Meta:
        model = JST

    @factory.post_generation
    def tree(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        JST.objects.rebuild()
        self.refresh_from_db()


class VoivodeshipJSTFactory(JednostkaAdministracyjnaFactory):
    category__level = 1


class CountyJSTFactory(JednostkaAdministracyjnaFactory):
    category__level = 2
    parent = factory.SubFactory(VoivodeshipJSTFactory)


class CommunityJSTFactory(JednostkaAdministracyjnaFactory):
    category__level = 3
    parent = factory.SubFactory(CountyJSTFactory)
