from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Monitoring


@admin.register(Monitoring)
class MonitoringAdmin(VersionAdmin):
    '''
        Admin View for Monitoring
    '''
    list_display = ('name', 'user')
    search_fields = ['name']
