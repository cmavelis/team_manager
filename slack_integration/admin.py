from django.contrib import admin

from .models import InteractiveMessage


class MessageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slack_message_ts', 'player_id', 'event_id']}),
    ]


admin.site.register(InteractiveMessage, MessageAdmin)
