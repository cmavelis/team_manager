from django.contrib import admin

from .models import Player, Event


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Info',              {'fields': ['nickname', 'first_name', 'last_name']}),
        ('Frisbee Info',  {'fields': ['field_position', 'gender_line']}),
        ]


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['name']}),
        ('Event Details',          {'fields': ['type', 'date',]}),# 'attendees']}),#
    ]


admin.site.register(Player, PlayerAdmin)
admin.site.register(Event, EventAdmin)

