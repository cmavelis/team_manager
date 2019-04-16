from django.db import models


class InteractiveMessage(models.Model):
    slack_message_ts = models.CharField(max_length=20)
    player_id = models.IntegerField(blank=True, null=True)
    event_id = models.IntegerField(blank=True, null=True)
