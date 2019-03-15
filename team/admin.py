from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Player, Event, User


class AttendeeInline(admin.TabularInline):
    model = Player.attending.through
    verbose_name = u"Attendance"
    verbose_name_plural = u"Attendance"


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Info',              {'fields': ['nickname', 'first_name', 'last_name']}),
        ('Frisbee Info',  {'fields': ['field_position', 'gender_line']}),
        ]
    inlines = (
        AttendeeInline,
    )


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['name']}),
        ('Event Details',          {'fields': ['type', 'date', ]}),
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Event, EventAdmin)

