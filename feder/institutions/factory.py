from autofixture import AutoFixture

from .models import Institution
from feder.teryt.factory import JSTFactory


def factory_institution(user):
    jst = JSTFactory()
    institution = AutoFixture(Institution,
                              field_values={'user': user, 'jst': jst}).create_one()
    return institution
