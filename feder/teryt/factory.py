from feder.teryt import models
from teryt_tree.factory import JednostkaAdministracyjnaFactory


class JSTFactory(JednostkaAdministracyjnaFactory):
    class Meta:
        model = models.JST
