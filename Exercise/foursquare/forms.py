from django.forms import ModelForm
from foursquare.models import LocationSearch

class LocationForm(ModelForm):
    class Meta:
        model = LocationSearch
        fields = ['food', 'location']
