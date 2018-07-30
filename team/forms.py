from django.forms import ModelForm
from .models import Player


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = '__all__'
