from teryt_tree.factories import JednostkaAdministracyjnaFactory

from feder.teryt import models


class JSTFactory(JednostkaAdministracyjnaFactory):
    class Meta:
        model = models.JST
