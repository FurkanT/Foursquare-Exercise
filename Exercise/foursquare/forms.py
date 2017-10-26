from django import forms
from django.forms import ModelForm
from foursquare.models import LocationSearch,Profile
from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget


class LocationForm(ModelForm):
    class Meta:
        model = LocationSearch
        fields = ['food', 'location']
        widgets = {'offset': HiddenInput()}


class SignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(input_formats=['%d/%m/%Y'])
    class Meta:     #date_of_birth = forms.DateField(SelectDateWidget(years=range(1900, 2100)))
        model = User
        fields = ('username', 'email', 'date_of_birth', 'password1', 'password2')


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(max_length=144)


class ImageUploadForm(forms.Form):
    avatar = forms.ImageField()
# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('date_of_birth',)
