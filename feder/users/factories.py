import factory

from feder.users import models


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence("user-{0}".format)
    email = factory.LazyAttribute(lambda o: "%s@example.com" % o.username)
    password = factory.PostGenerationMethodCall("set_password", "pass")

    class Meta:
        model = models.User
        django_get_or_create = ("username",)
