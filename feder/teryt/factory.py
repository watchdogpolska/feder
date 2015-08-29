from random import randint
from .models import JednostkaAdministracyjna as JST
from .models import Category


def factory_jst():
    category = Category.objects.create(name="X", level=1)
    return JST.objects.create(name="X", id=randint(0, 1000),
                              category=category,
                              updated_on='2015-05-12',
                              active=True)
