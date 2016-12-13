from solo.admin import SingletonModelAdmin
from django.contrib import admin
from django.contrib.auth.models import Group, User

from dsmr_backend.models.settings import BackendSettings

# Too bad there is no global admin.py, so we'll just disabled Group & User here.
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(BackendSettings)
class BackendSettingsAdmin(SingletonModelAdmin):
    list_display = ('data_retention_in_weeks', )
