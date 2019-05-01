from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from users.models import AppUser
from .models import Player, Attendance


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


class SignUpForm(UserCreationForm):
    class Meta:
        model = AppUser
        # TODO make this a combo form that puts extra fields into the Player model
        fields = [
                'email',
                'password1',
                'password2',
                # 'first_name',
                # 'last_name',
                ]
