from django.contrib import admin

from .models import Player, Event


class AttendeeInline(admin.TabularInline):
    model = Player.attending.through
    verbose_name = u"Attendance"
    verbose_name_plural = u"Attendance"


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'user', 'slack_user_id')
    fieldsets = [
        ('Personal Info', {'fields': ['nickname', 'first_name', 'last_name', 'user', 'slack_user_id']}),
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


admin.site.register(Player, PlayerAdmin)
admin.site.register(Event, EventAdmin)
