from django.forms import ModelForm
from foursquare.models import LocationSearch
from django.forms.widgets import HiddenInput


class LocationForm(ModelForm):
    class Meta:
        model = LocationSearch
        fields = ['food', 'location', 'offset']
        widgets = {'offset': HiddenInput()}
