import logging

from django.db.models.signals import post_save

from .models import Player, Event, Attendance

logger = logging.getLogger(__name__)


def player_created(sender, instance, created, **kwargs):
    if created:
        all_events = Event.objects.all()
        for event in all_events:
            Attendance.objects.create(event=event, player=instance)


def event_created(sender, instance, created, **kwargs):
    if created:
        all_players = Player.objects.all()
        for player in all_players:
            Attendance.objects.create(event=instance, player=player)


post_save.connect(player_created, sender=Player)
post_save.connect(event_created, sender=Event)
