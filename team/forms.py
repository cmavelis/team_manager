from django import forms
from django.forms import ModelForm
from .models import Player, Attendance, Event


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['first_name',
                  'last_name',
                  'nickname',
                  'gender_line',
                  'field_position',
                  ]


class AttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = ['status',
                  ]
        widgets = {'status': forms.RadioSelect}
