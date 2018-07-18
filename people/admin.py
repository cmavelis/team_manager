from django.contrib import admin

from .models import Player, Event


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Info',              {'fields': ['nickname', 'first_name', 'last_name']}),
        ('Frisbee Info',  {'fields': ['field_position', 'gender_line']}),
        ]
    # list_display = ('nickname', 'field_position',)


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['event_name']}),
        ('Event Details',          {'fields': ['type', 'date', 'attendees']}),
    ]
    # list_display = ('event_name', 'type', 'date',)


admin.site.register(Player, PlayerAdmin)
admin.site.register(Event, EventAdmin)

