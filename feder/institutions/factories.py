import factory

from feder.teryt.factories import JSTFactory

from .models import Institution, Tag


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("institution-{}".format)
    jst = factory.SubFactory(JSTFactory)
    email = factory.Sequence("email-{}@example.com".format)

    class Meta:
        model = Institution

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("tag-{}".format)

    class Meta:
        model = Tag
