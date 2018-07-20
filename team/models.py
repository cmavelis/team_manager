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
    name = models.CharField(max_length=30, default='')
    date = models.DateField('Event date')
    attendees = models.ManyToManyField(Player, through='Attendance')

    def __str__(self):
        return self.name


class Attendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    ATTENDANCE_TYPES = (
        ('Y', 'Yes',),
        ('N', 'No',),
        ('U', 'Unsure',),
        ('I', 'Injured',),
    )
    status = models.CharField(max_length=1, choices=ATTENDANCE_TYPES)
