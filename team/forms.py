from django import forms


class PersonalInfoForm(forms.Form):
    nickname = forms.CharField(label='Nickname (will identify you on this site)', max_length=20)
