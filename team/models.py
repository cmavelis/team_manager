from django.db import models


class Event(models.Model):
    # typical events for Ultimate teams -- may expand to include Practice, Social, Tryout, etc.
    EVENT_TYPES = (
        ('T', 'Tournament',),
        ('S', 'Scrimmage',),
    )

    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    name = models.CharField(max_length=30, default='')
    date = models.DateField('Event date')

    def __str__(self):
        return self.name


class Player(models.Model):
    # for Mixed Ultimate, players must play in one of two categories, defined in current USAU rules as Men and Women.
    # Baltimore BENCH has expanded this definition to be more inclusive, focusing on behavior rather than identity.
    # the terms F-line and M-line are specific, short, and descriptive. Most men would be M-line players; women, F-line
    # use them as you would O-line and D-line, for offense and defense
    # Examples: 1) That's Cameron, he's an M-line player.  2) I play on the F-line for Baltimore BENCH.

    GENDER_LINES = (
        ('F', 'F-line'),
        ('M', 'M-line'),
    )

    # typical positions used for playing Ultimate, including the less common "Hybrid", a mix of cutter/handler
    FIELD_POSITIONS = (
        ('C', 'Cutter'),
        ('H', 'Handler'),
        ('Y', 'Hybrid'),
    )

    # all the personal and Ultimate-related info we want to store
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    # Players will be identified by nickname throughout the model
    nickname = models.CharField(max_length=30, blank=True)
    gender_line = models.CharField(max_length=1, choices=GENDER_LINES)
    field_position = models.CharField(max_length=1, choices=FIELD_POSITIONS)

    # many-to-many relationship will be handled through the Attendance Class, a key component of this app
    attending = models.ManyToManyField(Event, through='Attendance')

    def __str__(self):
        return self.nickname

    def save(self, *args, **kwargs):
        if getattr(self, 'nickname', None) is '':  # check that current instance has 'nickname' attribute left blank
            self.nickname = self.first_name  # assign 'nickname' to be first name
        super(Player, self).save(*args, **kwargs)  # Call the "real" save() method.


class Attendance(models.Model):
    # connects Players to Events through a many-to-many relationship
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    # possible responses for Players to fill out their attendance
    # TODO: differentiate No into Excused/Absent?
    ATTENDANCE_TYPES = (
        ('Y', 'Yes',),
        ('N', 'No',),
        ('U', 'Unsure',),
        ('I', 'Injured',),
        ('P', 'Pending response',),
    )
    status = models.CharField(max_length=1, choices=ATTENDANCE_TYPES, default='P')
