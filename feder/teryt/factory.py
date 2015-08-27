from autofixture import AutoFixture
from .models import JednostkaAdministracyjna


def factory_jst():
    jst = AutoFixture(JednostkaAdministracyjna,
                      field_values={'updated_on': '2015-02-12'},
                      generate_fk=True).create_one(commit=False)
    jst.rght = 0
    jst.save()
    return jst
