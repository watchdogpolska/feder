from autofixture import AutoFixture

from feder.teryt.factory import factory_jst

from .models import Institution


def factory_institution(user):
    jst = factory_jst()
    institution = AutoFixture(Institution,
                              field_values={'user': user, 'jst': jst}).create_one()
    return institution
