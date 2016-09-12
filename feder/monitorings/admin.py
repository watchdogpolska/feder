from django.contrib import admin

from .models import Monitoring


@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    '''
        Admin View for Monitoring
    '''
    list_display = ('name', 'user')
    search_fields = ['name']
