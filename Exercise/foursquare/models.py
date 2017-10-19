from django.db import models


class LocationSearch(models.Model):
    food = models.CharField(max_length=100, )
    location = models.CharField(max_length=50, )
    search_date = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    # return self.food +" in "+ self.location
