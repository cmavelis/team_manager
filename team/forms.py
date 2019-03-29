from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Player, Attendance, User


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
    # TODO: add fields
    # birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')

    class Meta:
        model = User
        # TODO
        fields = [
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                ]
