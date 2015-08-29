from .models import JednostkaAdministracyjna as JST
from .models import Category

TERYT_COUNTER = 0


def factory_jst():
    global TERYT_COUNTER
    TERYT_COUNTER += 1
    category = Category.objects.create(name="X", level=1)
    return JST.objects.create(name="X", id=TERYT_COUNTER,
                              category=category,
                              updated_on='2015-05-12',
                              active=True)
