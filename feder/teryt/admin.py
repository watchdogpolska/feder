from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import JednostkaAdministracyjna


class JednostkaAdministracyjnaAdmin(MPTTModelAdmin):
    pass
admin.site.register(JednostkaAdministracyjna, JednostkaAdministracyjnaAdmin)
