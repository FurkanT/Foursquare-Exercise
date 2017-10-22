from django import forms
from django.forms import ModelForm
from foursquare.models import LocationSearch
from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LocationForm(ModelForm):
    class Meta:
        model = LocationSearch
        fields = ['food', 'location', 'offset']
        widgets = {'offset': HiddenInput()}


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
