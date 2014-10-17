from django.contrib import admin

from .models import Switch


class SwitchAdmin(admin.ModelAdmin):
    list_display = ('label', 'globally_active', 'description')
    list_editable = ('globally_active',)


admin.site.register(Switch, SwitchAdmin)
