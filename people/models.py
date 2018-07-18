from django.db import models


class Player(models.Model):
    GENDER_LINES = (
        ('F', 'F-line'),
        ('M', 'M-line'),
    )

    FIELD_POSITIONS = (
        ('C', 'Cutter'),
        ('H', 'Handler'),
        ('Y', 'Hybrid'),
    )

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30)
    gender_line = models.CharField(max_length=1, choices=GENDER_LINES)
    field_position = models.CharField(max_length=1, choices=FIELD_POSITIONS)

    def __str__(self):
        return self.nickname


class Event(models.Model):
    EVENT_TYPES = (
        ('T', 'Tournament',),
        ('S', 'Scrimmage',),
    )

    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=30, default='')
    date = models.DateField('tournament date')
    attendees = models.ManyToManyField(Player)

    def __str__(self):
        return self.event_name



