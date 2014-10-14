from django.contrib import admin

from .models import Switch


class SwitchAdmin(admin.ModelAdmin):
    list_display = ('label', 'globally_active', 'description')


admin.site.register(Switch, SwitchAdmin)
